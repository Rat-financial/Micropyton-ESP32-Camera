// Copyright 2020 Espressif Systems (Shanghai) PTE LTD
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include <stdint.h>

uint8_t bootloader_common_get_chip_revision(void)
{
    // should return the same value as esp_efuse_get_chip_ver()
    /* No other revisions for ESP32-S3 */
    return 0;
}

uint32_t bootloader_common_get_chip_ver_pkg(void)
{
    // should return the same value as esp_efuse_get_pkg_ver()
    return 0;
}
