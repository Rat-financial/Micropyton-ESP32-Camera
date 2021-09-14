/**
 * This file was generated by Apache newt version: 1.8.0-dev
 */

#ifndef H_MYNEWT_LOGCFG_
#define H_MYNEWT_LOGCFG_

#include "modlog/modlog.h"
#include "log_common/log_common.h"

#define BLE_HS_LOG_DEBUG(...) IGNORE(__VA_ARGS__)
#define BLE_HS_LOG_INFO(...) MODLOG_INFO(4, __VA_ARGS__)
#define BLE_HS_LOG_WARN(...) MODLOG_WARN(4, __VA_ARGS__)
#define BLE_HS_LOG_ERROR(...) MODLOG_ERROR(4, __VA_ARGS__)
#define BLE_HS_LOG_CRITICAL(...) MODLOG_CRITICAL(4, __VA_ARGS__)
#define BLE_HS_LOG_DISABLED(...) MODLOG_DISABLED(4, __VA_ARGS__)

#define BLE_MESH_ACCESS_LOG_DEBUG(...) IGNORE(__VA_ARGS__)
#define BLE_MESH_ACCESS_LOG_INFO(...) MODLOG_INFO(10, __VA_ARGS__)
#define BLE_MESH_ACCESS_LOG_WARN(...) MODLOG_WARN(10, __VA_ARGS__)
#define BLE_MESH_ACCESS_LOG_ERROR(...) MODLOG_ERROR(10, __VA_ARGS__)
#define BLE_MESH_ACCESS_LOG_CRITICAL(...) MODLOG_CRITICAL(10, __VA_ARGS__)
#define BLE_MESH_ACCESS_LOG_DISABLED(...) MODLOG_DISABLED(10, __VA_ARGS__)

#define BLE_MESH_ADV_LOG_DEBUG(...) IGNORE(__VA_ARGS__)
#define BLE_MESH_ADV_LOG_INFO(...) MODLOG_INFO(11, __VA_ARGS__)
#define BLE_MESH_ADV_LOG_WARN(...) MODLOG_WARN(11, __VA_ARGS__)
#define BLE_MESH_ADV_LOG_ERROR(...) MODLOG_ERROR(11, __VA_ARGS__)
#define BLE_MESH_ADV_LOG_CRITICAL(...) MODLOG_CRITICAL(11, __VA_ARGS__)
#define BLE_MESH_ADV_LOG_DISABLED(...) MODLOG_DISABLED(11, __VA_ARGS__)

#define BLE_MESH_BEACON_LOG_DEBUG(...) IGNORE(__VA_ARGS__)
#define BLE_MESH_BEACON_LOG_INFO(...) MODLOG_INFO(12, __VA_ARGS__)
#define BLE_MESH_BEACON_LOG_WARN(...) MODLOG_WARN(12, __VA_ARGS__)
#define BLE_MESH_BEACON_LOG_ERROR(...) MODLOG_ERROR(12, __VA_ARGS__)
#define BLE_MESH_BEACON_LOG_CRITICAL(...) MODLOG_CRITICAL(12, __VA_ARGS__)
#define BLE_MESH_BEACON_LOG_DISABLED(...) MODLOG_DISABLED(12, __VA_ARGS__)

#define BLE_MESH_CRYPTO_LOG_DEBUG(...) IGNORE(__VA_ARGS__)
#define BLE_MESH_CRYPTO_LOG_INFO(...) MODLOG_INFO(13, __VA_ARGS__)
#define BLE_MESH_CRYPTO_LOG_WARN(...) MODLOG_WARN(13, __VA_ARGS__)
#define BLE_MESH_CRYPTO_LOG_ERROR(...) MODLOG_ERROR(13, __VA_ARGS__)
#define BLE_MESH_CRYPTO_LOG_CRITICAL(...) MODLOG_CRITICAL(13, __VA_ARGS__)
#define BLE_MESH_CRYPTO_LOG_DISABLED(...) MODLOG_DISABLED(13, __VA_ARGS__)

#define BLE_MESH_FRIEND_LOG_DEBUG(...) IGNORE(__VA_ARGS__)
#define BLE_MESH_FRIEND_LOG_INFO(...) MODLOG_INFO(14, __VA_ARGS__)
#define BLE_MESH_FRIEND_LOG_WARN(...) MODLOG_WARN(14, __VA_ARGS__)
#define BLE_MESH_FRIEND_LOG_ERROR(...) MODLOG_ERROR(14, __VA_ARGS__)
#define BLE_MESH_FRIEND_LOG_CRITICAL(...) MODLOG_CRITICAL(14, __VA_ARGS__)
#define BLE_MESH_FRIEND_LOG_DISABLED(...) MODLOG_DISABLED(14, __VA_ARGS__)

#define BLE_MESH_LOG_DEBUG(...) IGNORE(__VA_ARGS__)
#define BLE_MESH_LOG_INFO(...) MODLOG_INFO(9, __VA_ARGS__)
#define BLE_MESH_LOG_WARN(...) MODLOG_WARN(9, __VA_ARGS__)
#define BLE_MESH_LOG_ERROR(...) MODLOG_ERROR(9, __VA_ARGS__)
#define BLE_MESH_LOG_CRITICAL(...) MODLOG_CRITICAL(9, __VA_ARGS__)
#define BLE_MESH_LOG_DISABLED(...) MODLOG_DISABLED(9, __VA_ARGS__)

#define BLE_MESH_LOW_POWER_LOG_DEBUG(...) IGNORE(__VA_ARGS__)
#define BLE_MESH_LOW_POWER_LOG_INFO(...) MODLOG_INFO(15, __VA_ARGS__)
#define BLE_MESH_LOW_POWER_LOG_WARN(...) MODLOG_WARN(15, __VA_ARGS__)
#define BLE_MESH_LOW_POWER_LOG_ERROR(...) MODLOG_ERROR(15, __VA_ARGS__)
#define BLE_MESH_LOW_POWER_LOG_CRITICAL(...) MODLOG_CRITICAL(15, __VA_ARGS__)
#define BLE_MESH_LOW_POWER_LOG_DISABLED(...) MODLOG_DISABLED(15, __VA_ARGS__)

#define BLE_MESH_MODEL_LOG_DEBUG(...) IGNORE(__VA_ARGS__)
#define BLE_MESH_MODEL_LOG_INFO(...) MODLOG_INFO(16, __VA_ARGS__)
#define BLE_MESH_MODEL_LOG_WARN(...) MODLOG_WARN(16, __VA_ARGS__)
#define BLE_MESH_MODEL_LOG_ERROR(...) MODLOG_ERROR(16, __VA_ARGS__)
#define BLE_MESH_MODEL_LOG_CRITICAL(...) MODLOG_CRITICAL(16, __VA_ARGS__)
#define BLE_MESH_MODEL_LOG_DISABLED(...) MODLOG_DISABLED(16, __VA_ARGS__)

#define BLE_MESH_NET_LOG_DEBUG(...) IGNORE(__VA_ARGS__)
#define BLE_MESH_NET_LOG_INFO(...) MODLOG_INFO(17, __VA_ARGS__)
#define BLE_MESH_NET_LOG_WARN(...) MODLOG_WARN(17, __VA_ARGS__)
#define BLE_MESH_NET_LOG_ERROR(...) MODLOG_ERROR(17, __VA_ARGS__)
#define BLE_MESH_NET_LOG_CRITICAL(...) MODLOG_CRITICAL(17, __VA_ARGS__)
#define BLE_MESH_NET_LOG_DISABLED(...) MODLOG_DISABLED(17, __VA_ARGS__)

#define BLE_MESH_PROV_LOG_DEBUG(...) IGNORE(__VA_ARGS__)
#define BLE_MESH_PROV_LOG_INFO(...) MODLOG_INFO(18, __VA_ARGS__)
#define BLE_MESH_PROV_LOG_WARN(...) MODLOG_WARN(18, __VA_ARGS__)
#define BLE_MESH_PROV_LOG_ERROR(...) MODLOG_ERROR(18, __VA_ARGS__)
#define BLE_MESH_PROV_LOG_CRITICAL(...) MODLOG_CRITICAL(18, __VA_ARGS__)
#define BLE_MESH_PROV_LOG_DISABLED(...) MODLOG_DISABLED(18, __VA_ARGS__)

#define BLE_MESH_PROXY_LOG_DEBUG(...) IGNORE(__VA_ARGS__)
#define BLE_MESH_PROXY_LOG_INFO(...) MODLOG_INFO(19, __VA_ARGS__)
#define BLE_MESH_PROXY_LOG_WARN(...) MODLOG_WARN(19, __VA_ARGS__)
#define BLE_MESH_PROXY_LOG_ERROR(...) MODLOG_ERROR(19, __VA_ARGS__)
#define BLE_MESH_PROXY_LOG_CRITICAL(...) MODLOG_CRITICAL(19, __VA_ARGS__)
#define BLE_MESH_PROXY_LOG_DISABLED(...) MODLOG_DISABLED(19, __VA_ARGS__)

#define BLE_MESH_SETTINGS_LOG_DEBUG(...) IGNORE(__VA_ARGS__)
#define BLE_MESH_SETTINGS_LOG_INFO(...) MODLOG_INFO(20, __VA_ARGS__)
#define BLE_MESH_SETTINGS_LOG_WARN(...) MODLOG_WARN(20, __VA_ARGS__)
#define BLE_MESH_SETTINGS_LOG_ERROR(...) MODLOG_ERROR(20, __VA_ARGS__)
#define BLE_MESH_SETTINGS_LOG_CRITICAL(...) MODLOG_CRITICAL(20, __VA_ARGS__)
#define BLE_MESH_SETTINGS_LOG_DISABLED(...) MODLOG_DISABLED(20, __VA_ARGS__)

#define BLE_MESH_TRANS_LOG_DEBUG(...) IGNORE(__VA_ARGS__)
#define BLE_MESH_TRANS_LOG_INFO(...) MODLOG_INFO(21, __VA_ARGS__)
#define BLE_MESH_TRANS_LOG_WARN(...) MODLOG_WARN(21, __VA_ARGS__)
#define BLE_MESH_TRANS_LOG_ERROR(...) MODLOG_ERROR(21, __VA_ARGS__)
#define BLE_MESH_TRANS_LOG_CRITICAL(...) MODLOG_CRITICAL(21, __VA_ARGS__)
#define BLE_MESH_TRANS_LOG_DISABLED(...) MODLOG_DISABLED(21, __VA_ARGS__)

#define DFLT_LOG_DEBUG(...) IGNORE(__VA_ARGS__)
#define DFLT_LOG_INFO(...) MODLOG_INFO(0, __VA_ARGS__)
#define DFLT_LOG_WARN(...) MODLOG_WARN(0, __VA_ARGS__)
#define DFLT_LOG_ERROR(...) MODLOG_ERROR(0, __VA_ARGS__)
#define DFLT_LOG_CRITICAL(...) MODLOG_CRITICAL(0, __VA_ARGS__)
#define DFLT_LOG_DISABLED(...) MODLOG_DISABLED(0, __VA_ARGS__)

#define MFG_LOG_DEBUG(...) IGNORE(__VA_ARGS__)
#define MFG_LOG_INFO(...) IGNORE(__VA_ARGS__)
#define MFG_LOG_WARN(...) IGNORE(__VA_ARGS__)
#define MFG_LOG_ERROR(...) IGNORE(__VA_ARGS__)
#define MFG_LOG_CRITICAL(...) IGNORE(__VA_ARGS__)
#define MFG_LOG_DISABLED(...) MODLOG_DISABLED(128, __VA_ARGS__)

#endif