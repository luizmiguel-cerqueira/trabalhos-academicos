#ifndef DS_API_H
#define DS_API_H

#include <stdint.h>

#ifdef _WIN32
#define DS_API __declspec(dllexport)
#else
#define DS_API
#endif

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DS_OK = 0,
    DS_INVALID_ARGUMENT = 1,
    DS_FULL = 2,
    DS_EMPTY = 3,
    DS_NOT_FOUND = 4,
    DS_OUT_OF_MEMORY = 5,
    DS_BUFFER_TOO_SMALL = 6,
    DS_UNSUPPORTED_OPERATION = 7,
    DS_OUT_OF_RANGE = 8
};

enum {
    DS_KIND_QUEUE = 1,
    DS_KIND_STACK = 2,
    DS_KIND_LIST = 3
};

enum {
    DS_ACTION_INSERT = 1,
    DS_ACTION_REMOVE_FIRST = 2,
    DS_ACTION_REMOVE_BY_VALUE = 3,
    DS_ACTION_CLEAR = 4
};

typedef void *ds_handle;

DS_API uint32_t ds_api_version(void);
DS_API int32_t ds_create(ds_handle *out_context);
DS_API void ds_destroy(ds_handle context);
DS_API uint32_t ds_capacity(void);
DS_API int32_t ds_insert(ds_handle context, int32_t kind, int32_t value);
DS_API int32_t ds_remove_first(ds_handle context, int32_t kind, int32_t *out_value);
DS_API int32_t ds_remove_value(ds_handle context, int32_t kind, int32_t value);
DS_API int32_t ds_clear(ds_handle context, int32_t kind, uint32_t *out_removed);
DS_API int32_t ds_copy_values(
    ds_handle context,
    int32_t kind,
    int32_t *buffer,
    uint32_t buffer_capacity,
    uint32_t *out_count
);
DS_API int32_t ds_log_count(ds_handle context, uint64_t *out_count);
DS_API int32_t ds_log_read(
    ds_handle context,
    uint64_t start_index,
    uint32_t max_items,
    uint64_t *sequences,
    int32_t *kinds,
    int32_t *actions,
    int32_t *values,
    uint32_t *quantities,
    uint32_t *out_written
);

#ifdef __cplusplus
}
#endif

#endif
