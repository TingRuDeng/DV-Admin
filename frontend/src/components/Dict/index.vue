<template>
  <el-select
    v-if="type === 'select'"
    v-model="selectedScalarValue"
    :placeholder="placeholder"
    :disabled="disabled"
    clearable
    :style="style"
    @change="handleScalarChange"
  >
    <el-option
      v-for="option in options"
      :key="option.value"
      :label="option.label"
      :value="option.value"
    />
  </el-select>

  <el-radio-group
    v-else-if="type === 'radio'"
    v-model="selectedScalarValue"
    :disabled="disabled"
    :style="style"
    @change="handleScalarChange"
  >
    <el-radio v-for="option in options" :key="option.value" :value="option.value">
      {{ option.label }}
    </el-radio>
  </el-radio-group>

  <el-checkbox-group
    v-else-if="type === 'checkbox'"
    v-model="selectedCheckboxValues"
    :disabled="disabled"
    :style="style"
    @change="handleCheckboxChange"
  >
    <el-checkbox v-for="option in options" :key="option.value" :value="option.value">
      {{ option.label }}
    </el-checkbox>
  </el-checkbox-group>
</template>

<script setup lang="ts">
import type { CheckboxValueType } from "element-plus";

import { useDictStore } from "@/store";
import type { DictModelValue, DictValue } from "@/components/Dict/types";

const dictStore = useDictStore();

const props = defineProps({
  code: {
    type: String,
    required: true,
  },
  modelValue: {
    type: [String, Number, Array],
    required: false,
  },
  type: {
    type: String,
    default: "select",
    validator: (value: string) => ["select", "radio", "checkbox"].includes(value),
  },
  placeholder: {
    type: String,
    default: "请选择",
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  style: {
    type: Object,
    default: () => {
      return {
        width: "300px",
      };
    },
  },
});

const emit = defineEmits(["update:modelValue"]);

const options = ref<Array<{ label: string; value: string | number }>>([]);

const selectedValue = ref<DictModelValue>(normalizeModelValue(props.modelValue));

const selectedScalarValue = computed({
  get() {
    return Array.isArray(selectedValue.value) ? undefined : selectedValue.value;
  },
  set(value: DictValue | undefined) {
    selectedValue.value = value;
  },
});

const selectedCheckboxValues = computed({
  get() {
    return Array.isArray(selectedValue.value) ? selectedValue.value : [];
  },
  set(value: DictValue[]) {
    selectedValue.value = value;
  },
});

function isDictValue(value: unknown): value is DictValue {
  return typeof value === "string" || typeof value === "number";
}

function normalizeModelValue(value: unknown): DictModelValue {
  if (isDictValue(value)) {
    return value;
  }

  if (Array.isArray(value)) {
    return value.filter(isDictValue);
  }

  return undefined;
}

function normalizeCheckboxValues(values: unknown[]) {
  return values.filter(isDictValue);
}

// 监听 modelValue 和 options 的变化
watch(
  [() => props.modelValue, () => options.value],
  ([newValue, newOptions]) => {
    if (newOptions.length > 0 && newValue !== undefined) {
      if (props.type === "checkbox") {
        selectedValue.value = Array.isArray(newValue) ? normalizeCheckboxValues(newValue) : [];
      } else {
        const matchedOption = newOptions.find(
          (option) => String(option.value) === String(newValue)
        );
        selectedValue.value = matchedOption?.value;
      }
    } else {
      selectedValue.value = undefined;
    }
  },
  { immediate: true }
);

// 监听 selectedValue 的变化并触发 update:modelValue
function handleScalarChange(value: string | number | boolean | undefined) {
  emit("update:modelValue", isDictValue(value) ? value : undefined);
}

function handleCheckboxChange(values: CheckboxValueType[]) {
  emit("update:modelValue", normalizeCheckboxValues(values));
}

// 获取字典数据
onMounted(async () => {
  await dictStore.loadDictItems(props.code);
  options.value = dictStore.getDictItems(props.code);
});
</script>
