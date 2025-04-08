#!/bin/sh
set -x
# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
BOOTINFO_SD="${SRCDIR}/bootinfo_sd.bin"
FSBL="${SRCDIR}/FSBL.bin"
UBOOT_ENV="${SRCDIR}/u-boot-env-default.bin"
OPENSBI="${SRCDIR}/u-boot-opensbi.itb"

# Check if U-Boot SPL file exists
if [ ! -f "$BOOTINFO_SD" ]; then
    printf "\n"
    printf "+-----------------------------+\n"
    printf "|       _                 _   |\n"
    printf "| _   _| |__   ___   ___ | |_ |\n"
    printf "|| | | | '_ \ / _ \ / _ \| __||\n"
    printf "|| |_| | |_) | (_) | (_) | |_ |\n"
    printf "| \__,_|_.__/ \___/ \___/ \__||\n"
    printf "+-----------------------------+\n"
    printf "\n"
    printf "  ⚠️  U-BOOT filepart bootinfo_sd.bin is missing!  ⚠️\n"
    printf "  Please compile bootloader before running this script.\n"
    printf "\n"
    exit 0
fi

pushd "${OUTPUTDIR}"
printf "Writing bootloader to the image...\n"
dd if=${BOOTINFO_SD} of=image.raw seek=0 conv=notrunc
dd if=${FSBL} of=image.raw seek=256 conv=notrunc
dd if=${UBOOT_ENV} of=image.raw seek=768 conv=notrunc
dd if=${OPENSBI} of=image.raw seek=1664 conv=notrunc
popd
