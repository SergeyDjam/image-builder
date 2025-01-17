#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import shutil
#from common import load_config

def get_kernel_version(kernel_dir):
    """Extract kernel version by running 'make kernelversion' in the kernel directory."""
    try:
        result = subprocess.run(
            ["make", "kernelversion"],
            cwd=kernel_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to get kernel version from {kernel_dir}")
        print(e.stderr)
        sys.exit(1)


def generate_spec_file(TMP_DIR, config, vendor, device):
    """Generate RPM spec file from template and config"""
    # Load device config
    config_path = os.path.join("device", vendor, device, "config")
    if not os.path.exists(config_path):
        print(f"Error: Config file not found at {config_path}")
        sys.exit(1)

    # Load template
    template_path = os.path.join("utils", "kernel.template")
    if not os.path.exists(template_path):
        print(f"Error: Template file not found at {template_path}")
        sys.exit(1)

    with open(template_path, 'r') as f:
        template = f.read()

    # Extract kernel version from kernel URL and branch
    kernel_url, kernel_branch = config["KERNEL"].split("#")

    # Extract kernel version from Makefile
    kernel_dir = os.path.join(TMP_DIR, vendor, device, "kernel")
    if not os.path.exists(kernel_dir):
        print(f"Error: Kernel directory not found at {kernel_dir}")
        sys.exit(1)

    kernel_version = get_kernel_version(kernel_dir)

    # Determine KERNEL_ARCH and CROSS_COMPILE based on ARCH
    arch = config.get("ARCH", "unknown")
    kernel_config = config.get("KERNEL_CONFIG", "unknown")
    if arch == "aarch64":
        kernel_arch = "arm64"
        cross_compile = "aarch64-linux-gnu"
    else:
        kernel_arch = arch
        cross_compile = f"{arch}-linux-gnu"  # Default cross compile format

    # Prepare replacements
    device_name = f"{vendor}-{device}"
    replacements = {
        "{BOARD_NAME}": device_name,
        "{KERNEL_VERSION}": kernel_version,
        "{DEVICE_NAME}": device_name,
        "{KERNEL_ARCH}": kernel_arch,
        "{ARCH}": arch,  # Add ARCH replacement
        "{KERNEL_CONFIG}": kernel_config,
        "{CROSS_COMPILE}": cross_compile  # Add CROSS_COMPILE replacement
    }

    # Handle Source1 based on PRESET_CONFIG
    preset_config = config.get("PRESET_CONFIG", "").strip()
    if preset_config:
        replacements["{Source1}"] = f"Source1: {preset_config}"  # Format Source1 correctly
        replacements["{SOURCE1_COMMAND}"] = "cp %{S:1} .config"
    else:
        replacements["{Source1}"] = ""  # Leave Source1 empty if PRESET_CONFIG is not set
        replacements["{SOURCE1_COMMAND}"] = ""

    kernel_defconfig = config.get("KERNEL_CONFIG", "").strip()
    if kernel_defconfig:
        replacements["{MAKE_DEFCONFIG}"] = f"%make_build {kernel_defconfig} ARCH={kernel_arch}"  # Format Source1 correctly
    else:
        replacements["{MAKE_DEFCONFIG}"] = ""

    # Apply replacements
    spec_content = template
    for key, value in replacements.items():
        spec_content = spec_content.replace(key, value)

    # Define output directory and path
    output_dir = os.path.join(TMP_DIR, vendor, device, "kernel-build")
    os.makedirs(output_dir, exist_ok=True)
    # Copy PRESET_CONFIG file if it exists
    if preset_config:
        preset_config_path = os.path.join("device", vendor, device, preset_config)
        if os.path.exists(preset_config_path):
            shutil.copy(preset_config_path, output_dir)
            print(f"Copied {preset_config} to {output_dir}")
        else:
            print(f"Warning: PRESET_CONFIG file {preset_config_path} not found.")

    # Write spec file
    spec_file_path = os.path.join(output_dir, f"kernel-{device_name}.spec")
    with open(spec_file_path, 'w') as f:
        f.write(spec_content)

    print(f"Generated spec file: {spec_file_path}")
    return spec_file_path

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: generate_spec.py <vendor> <device>")
        sys.exit(1)

    vendor = sys.argv[1]
    device = sys.argv[2]

    generate_spec_file(vendor, device)

