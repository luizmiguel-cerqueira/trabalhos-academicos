#include "ds_api.h"

#include <limits.h>
#include <stdlib.h>

#define DS_QUEUE_CAPACITY 10u

struct queue_node {
    int32_t value;
    struct queue_node *next;
};

struct log_entry {
    uint64_t sequence;
    int32_t kind;
    int32_t action;
    int32_t value;
    uint32_t quantity;
    struct log_entry *next;
};

struct ds_context {
    struct queue_node *first;
    struct queue_node *last;
    uint32_t size;
    struct log_entry *log_first;
    struct log_entry *log_last;
    uint64_t log_count;
};

static int valid_kind(int32_t kind)
{
    return kind == DS_KIND_QUEUE || kind == DS_KIND_STACK || kind == DS_KIND_LIST;
}

static int queue_kind(int32_t kind)
{
    return kind == DS_KIND_QUEUE;
}

static struct log_entry *new_log(
    const struct ds_context *context,
    int32_t action,
    int32_t value,
    uint32_t quantity
)
{
    struct log_entry *entry;

    if (context->log_count == UINT64_MAX) {
        return NULL;
    }
    entry = (struct log_entry *)malloc(sizeof(*entry));
    if (entry == NULL) {
        return NULL;
    }
    entry->sequence = context->log_count + 1u;
    entry->kind = DS_KIND_QUEUE;
    entry->action = action;
    entry->value = value;
    entry->quantity = quantity;
    entry->next = NULL;
    return entry;
}

static void append_log(struct ds_context *context, struct log_entry *entry)
{
    if (context->log_last == NULL) {
        context->log_first = entry;
    } else {
        context->log_last->next = entry;
    }
    context->log_last = entry;
    context->log_count++;
}

DS_API uint32_t ds_api_version(void)
{
    return 1u;
}

DS_API int32_t ds_create(ds_handle *out_context)
{
    struct ds_context *context;

    if (out_context == NULL) {
        return DS_INVALID_ARGUMENT;
    }
    *out_context = NULL;
    context = (struct ds_context *)calloc(1u, sizeof(*context));
    if (context == NULL) {
        return DS_OUT_OF_MEMORY;
    }
    *out_context = context;
    return DS_OK;
}

DS_API void ds_destroy(ds_handle handle)
{
    struct ds_context *context = (struct ds_context *)handle;
    struct queue_node *node;
    struct log_entry *entry;

    if (context == NULL) {
        return;
    }
    while (context->first != NULL) {
        node = context->first;
        context->first = node->next;
        free(node);
    }
    while (context->log_first != NULL) {
        entry = context->log_first;
        context->log_first = entry->next;
        free(entry);
    }
    free(context);
}

DS_API uint32_t ds_capacity(void)
{
    return DS_QUEUE_CAPACITY;
}

DS_API int32_t ds_insert(ds_handle handle, int32_t kind, int32_t value)
{
    struct ds_context *context = (struct ds_context *)handle;
    struct queue_node *node;
    struct log_entry *entry;

    if (context == NULL || !valid_kind(kind)) {
        return DS_INVALID_ARGUMENT;
    }
    if (!queue_kind(kind)) {
        return DS_UNSUPPORTED_OPERATION;
    }
    if (context->size >= DS_QUEUE_CAPACITY) {
        return DS_FULL;
    }
    node = (struct queue_node *)malloc(sizeof(*node));
    if (node == NULL) {
        return DS_OUT_OF_MEMORY;
    }
    entry = new_log(context, DS_ACTION_INSERT, value, 1u);
    if (entry == NULL) {
        free(node);
        return context->log_count == UINT64_MAX ? DS_OUT_OF_RANGE : DS_OUT_OF_MEMORY;
    }
    node->value = value;
    node->next = NULL;
    if (context->last == NULL) {
        context->first = node;
    } else {
        context->last->next = node;
    }
    context->last = node;
    context->size++;
    append_log(context, entry);
    return DS_OK;
}

DS_API int32_t ds_remove_first(ds_handle handle, int32_t kind, int32_t *out_value)
{
    struct ds_context *context = (struct ds_context *)handle;
    struct queue_node *node;
    struct log_entry *entry;

    if (context == NULL || !valid_kind(kind) || out_value == NULL) {
        return DS_INVALID_ARGUMENT;
    }
    if (!queue_kind(kind)) {
        return DS_UNSUPPORTED_OPERATION;
    }
    if (context->first == NULL) {
        return DS_EMPTY;
    }
    node = context->first;
    entry = new_log(context, DS_ACTION_REMOVE_FIRST, node->value, 1u);
    if (entry == NULL) {
        return context->log_count == UINT64_MAX ? DS_OUT_OF_RANGE : DS_OUT_OF_MEMORY;
    }
    context->first = node->next;
    if (context->first == NULL) {
        context->last = NULL;
    }
    context->size--;
    *out_value = node->value;
    free(node);
    append_log(context, entry);
    return DS_OK;
}

DS_API int32_t ds_remove_value(ds_handle handle, int32_t kind, int32_t value)
{
    if (handle == NULL || !valid_kind(kind)) {
        return DS_INVALID_ARGUMENT;
    }
    (void)value;
    return DS_UNSUPPORTED_OPERATION;
}

DS_API int32_t ds_clear(ds_handle handle, int32_t kind, uint32_t *out_removed)
{
    struct ds_context *context = (struct ds_context *)handle;
    struct queue_node *node;
    struct log_entry *entry;
    uint32_t removed;

    if (context == NULL || !valid_kind(kind) || out_removed == NULL) {
        return DS_INVALID_ARGUMENT;
    }
    if (!queue_kind(kind)) {
        return DS_UNSUPPORTED_OPERATION;
    }
    if (context->first == NULL) {
        return DS_EMPTY;
    }
    removed = context->size;
    entry = new_log(context, DS_ACTION_CLEAR, 0, removed);
    if (entry == NULL) {
        return context->log_count == UINT64_MAX ? DS_OUT_OF_RANGE : DS_OUT_OF_MEMORY;
    }
    while (context->first != NULL) {
        node = context->first;
        context->first = node->next;
        free(node);
    }
    context->last = NULL;
    context->size = 0;
    *out_removed = removed;
    append_log(context, entry);
    return DS_OK;
}

DS_API int32_t ds_copy_values(
    ds_handle handle,
    int32_t kind,
    int32_t *buffer,
    uint32_t buffer_capacity,
    uint32_t *out_count
)
{
    struct ds_context *context = (struct ds_context *)handle;
    struct queue_node *node;
    uint32_t index = 0;

    if (context == NULL || !valid_kind(kind) || out_count == NULL) {
        return DS_INVALID_ARGUMENT;
    }
    if (!queue_kind(kind)) {
        return DS_UNSUPPORTED_OPERATION;
    }
    if (buffer == NULL && buffer_capacity != 0u) {
        return DS_INVALID_ARGUMENT;
    }
    *out_count = context->size;
    if (buffer == NULL && buffer_capacity == 0u) {
        return DS_OK;
    }
    if (buffer_capacity < context->size) {
        return DS_BUFFER_TOO_SMALL;
    }
    node = context->first;
    while (node != NULL) {
        buffer[index++] = node->value;
        node = node->next;
    }
    return DS_OK;
}

DS_API int32_t ds_log_count(ds_handle handle, uint64_t *out_count)
{
    struct ds_context *context = (struct ds_context *)handle;

    if (context == NULL || out_count == NULL) {
        return DS_INVALID_ARGUMENT;
    }
    *out_count = context->log_count;
    return DS_OK;
}

DS_API int32_t ds_log_read(
    ds_handle handle,
    uint64_t start_index,
    uint32_t max_items,
    uint64_t *sequences,
    int32_t *kinds,
    int32_t *actions,
    int32_t *values,
    uint32_t *quantities,
    uint32_t *out_written
)
{
    struct ds_context *context = (struct ds_context *)handle;
    struct log_entry *entry;
    uint64_t index = 0;
    uint32_t written = 0;

    if (context == NULL || max_items == 0u || max_items > 100u ||
        sequences == NULL || kinds == NULL || actions == NULL ||
        values == NULL || quantities == NULL || out_written == NULL) {
        return DS_INVALID_ARGUMENT;
    }
    if (start_index > context->log_count) {
        return DS_OUT_OF_RANGE;
    }
    entry = context->log_first;
    while (entry != NULL && index < start_index) {
        entry = entry->next;
        index++;
    }
    while (entry != NULL && written < max_items) {
        sequences[written] = entry->sequence;
        kinds[written] = entry->kind;
        actions[written] = entry->action;
        values[written] = entry->value;
        quantities[written] = entry->quantity;
        entry = entry->next;
        written++;
    }
    *out_written = written;
    return DS_OK;
}
