#include "ds_api.h"

#include <limits.h>
#include <stdlib.h>

#define DS_QUEUE_CAPACITY 10u

typedef struct ds_node {
    int32_t value;
    struct ds_node *next;
} ds_node;

typedef struct ds_chain {
    ds_node *first;
    ds_node *last;
    uint32_t size;
} ds_chain;

typedef struct ds_log_entry {
    uint64_t sequence;
    int32_t kind;
    int32_t action;
    int32_t value;
    uint32_t quantity;
    struct ds_log_entry *next;
} ds_log_entry;

typedef struct ds_context {
    ds_chain chains[4];
    ds_log_entry *log_first;
    ds_log_entry *log_last;
    uint64_t log_count;
} ds_context;

static int valid_kind(int32_t kind)
{
    return kind == DS_KIND_QUEUE || kind == DS_KIND_STACK || kind == DS_KIND_LIST;
}

static ds_chain *get_chain(ds_context *context, int32_t kind)
{
    return &context->chains[kind];
}

static ds_log_entry *new_log(
    const ds_context *context,
    int32_t kind,
    int32_t action,
    int32_t value,
    uint32_t quantity
)
{
    ds_log_entry *entry;

    if (context->log_count == UINT64_MAX) {
        return NULL;
    }
    entry = (ds_log_entry *)malloc(sizeof(*entry));
    if (entry == NULL) {
        return NULL;
    }
    entry->sequence = context->log_count + 1u;
    entry->kind = kind;
    entry->action = action;
    entry->value = value;
    entry->quantity = quantity;
    entry->next = NULL;
    return entry;
}

static void append_log(ds_context *context, ds_log_entry *entry)
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
    ds_context *context;

    if (out_context == NULL) {
        return DS_INVALID_ARGUMENT;
    }
    *out_context = NULL;
    context = (ds_context *)calloc(1u, sizeof(*context));
    if (context == NULL) {
        return DS_OUT_OF_MEMORY;
    }
    *out_context = context;
    return DS_OK;
}

DS_API void ds_destroy(ds_handle handle)
{
    ds_context *context = (ds_context *)handle;
    ds_log_entry *entry;
    int32_t kind;

    if (context == NULL) {
        return;
    }
    for (kind = DS_KIND_QUEUE; kind <= DS_KIND_LIST; kind++) {
        ds_node *node = context->chains[kind].first;
        while (node != NULL) {
            ds_node *next = node->next;
            free(node);
            node = next;
        }
    }
    entry = context->log_first;
    while (entry != NULL) {
        ds_log_entry *next = entry->next;
        free(entry);
        entry = next;
    }
    free(context);
}

DS_API uint32_t ds_capacity(void)
{
    return DS_QUEUE_CAPACITY;
}

DS_API int32_t ds_insert(ds_handle handle, int32_t kind, int32_t value)
{
    ds_context *context = (ds_context *)handle;
    ds_chain *chain;
    ds_node *node;
    ds_log_entry *entry;

    if (context == NULL || !valid_kind(kind)) {
        return DS_INVALID_ARGUMENT;
    }
    chain = get_chain(context, kind);
    if (chain->size >= DS_QUEUE_CAPACITY) {
        return DS_FULL;
    }
    node = (ds_node *)malloc(sizeof(*node));
    if (node == NULL) {
        return DS_OUT_OF_MEMORY;
    }
    entry = new_log(context, kind, DS_ACTION_INSERT, value, 1u);
    if (entry == NULL) {
        free(node);
        return context->log_count == UINT64_MAX ? DS_OUT_OF_RANGE : DS_OUT_OF_MEMORY;
    }
    node->value = value;
    node->next = NULL;
    if (kind == DS_KIND_STACK) {
        node->next = chain->first;
        chain->first = node;
        if (chain->last == NULL) {
            chain->last = node;
        }
    } else {
        if (chain->last == NULL) {
            chain->first = node;
        } else {
            chain->last->next = node;
        }
        chain->last = node;
    }
    chain->size++;
    append_log(context, entry);
    return DS_OK;
}

DS_API int32_t ds_remove_first(ds_handle handle, int32_t kind, int32_t *out_value)
{
    ds_context *context = (ds_context *)handle;
    ds_chain *chain;
    ds_node *node;
    ds_log_entry *entry;

    if (context == NULL || !valid_kind(kind) || out_value == NULL) {
        return DS_INVALID_ARGUMENT;
    }
    chain = get_chain(context, kind);
    if (chain->first == NULL) {
        return DS_EMPTY;
    }
    node = chain->first;
    entry = new_log(context, kind, DS_ACTION_REMOVE_FIRST, node->value, 1u);
    if (entry == NULL) {
        return context->log_count == UINT64_MAX ? DS_OUT_OF_RANGE : DS_OUT_OF_MEMORY;
    }
    chain->first = node->next;
    if (chain->first == NULL) {
        chain->last = NULL;
    }
    chain->size--;
    *out_value = node->value;
    free(node);
    append_log(context, entry);
    return DS_OK;
}

DS_API int32_t ds_remove_value(ds_handle handle, int32_t kind, int32_t value)
{
    ds_context *context = (ds_context *)handle;
    ds_chain *chain;
    ds_node *previous = NULL;
    ds_node *current;
    ds_log_entry *entry;

    if (context == NULL || !valid_kind(kind)) {
        return DS_INVALID_ARGUMENT;
    }
    if (kind != DS_KIND_LIST) {
        return DS_UNSUPPORTED_OPERATION;
    }
    chain = get_chain(context, kind);
    current = chain->first;
    while (current != NULL && current->value != value) {
        previous = current;
        current = current->next;
    }
    if (current == NULL) {
        return chain->first == NULL ? DS_EMPTY : DS_NOT_FOUND;
    }
    entry = new_log(context, kind, DS_ACTION_REMOVE_BY_VALUE, value, 1u);
    if (entry == NULL) {
        return context->log_count == UINT64_MAX ? DS_OUT_OF_RANGE : DS_OUT_OF_MEMORY;
    }
    if (previous == NULL) {
        chain->first = current->next;
    } else {
        previous->next = current->next;
    }
    if (chain->last == current) {
        chain->last = previous;
    }
    chain->size--;
    free(current);
    append_log(context, entry);
    return DS_OK;
}

DS_API int32_t ds_clear(ds_handle handle, int32_t kind, uint32_t *out_removed)
{
    ds_context *context = (ds_context *)handle;
    ds_chain *chain;
    ds_log_entry *entry;
    ds_node *node;
    uint32_t removed;

    if (context == NULL || !valid_kind(kind) || out_removed == NULL) {
        return DS_INVALID_ARGUMENT;
    }
    chain = get_chain(context, kind);
    if (chain->first == NULL) {
        return DS_EMPTY;
    }
    removed = chain->size;
    entry = new_log(context, kind, DS_ACTION_CLEAR, 0, removed);
    if (entry == NULL) {
        return context->log_count == UINT64_MAX ? DS_OUT_OF_RANGE : DS_OUT_OF_MEMORY;
    }
    node = chain->first;
    while (node != NULL) {
        ds_node *next = node->next;
        free(node);
        node = next;
    }
    chain->first = NULL;
    chain->last = NULL;
    chain->size = 0;
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
    ds_context *context = (ds_context *)handle;
    ds_node *node;
    ds_chain *chain;
    uint32_t index = 0;

    if (context == NULL || !valid_kind(kind) || out_count == NULL) {
        return DS_INVALID_ARGUMENT;
    }
    if (buffer == NULL && buffer_capacity != 0u) {
        return DS_INVALID_ARGUMENT;
    }
    chain = get_chain(context, kind);
    *out_count = chain->size;
    if (buffer == NULL && buffer_capacity == 0u) {
        return DS_OK;
    }
    if (buffer_capacity < chain->size) {
        return DS_BUFFER_TOO_SMALL;
    }
    node = chain->first;
    while (node != NULL) {
        buffer[index++] = node->value;
        node = node->next;
    }
    return DS_OK;
}

DS_API int32_t ds_log_count(ds_handle handle, uint64_t *out_count)
{
    ds_context *context = (ds_context *)handle;

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
    ds_context *context = (ds_context *)handle;
    ds_log_entry *entry;
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
