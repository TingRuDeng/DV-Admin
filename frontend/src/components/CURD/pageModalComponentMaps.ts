import {
  ElCascader,
  ElCheckbox,
  ElCheckboxGroup,
  ElDatePicker,
  ElInput,
  ElInputNumber,
  ElOption,
  ElRadio,
  ElRadioGroup,
  ElSelect,
  ElSwitch,
  ElText,
  ElTimePicker,
  ElTimeSelect,
  ElTreeSelect,
} from "element-plus";
import { markRaw } from "vue";

import IconSelect from "@/components/IconSelect/index.vue";
import InputTag from "@/components/InputTag/index.vue";

import type { IComponentType, ICurdComponentMap, ICurdComponentMapValue } from "./types";

export const componentMap: ICurdComponentMap<IComponentType> = new Map<
  IComponentType,
  ICurdComponentMapValue
>([
  ["input", markRaw(ElInput)],
  ["select", markRaw(ElSelect)],
  ["switch", markRaw(ElSwitch)],
  ["cascader", markRaw(ElCascader)],
  ["input-number", markRaw(ElInputNumber)],
  ["input-tag", markRaw(InputTag)],
  ["time-picker", markRaw(ElTimePicker)],
  ["time-select", markRaw(ElTimeSelect)],
  ["date-picker", markRaw(ElDatePicker)],
  ["tree-select", markRaw(ElTreeSelect)],
  ["custom-tag", markRaw(InputTag)],
  ["text", markRaw(ElText)],
  ["radio", markRaw(ElRadioGroup)],
  ["checkbox", markRaw(ElCheckboxGroup)],
  ["icon-select", markRaw(IconSelect)],
  ["custom", ""],
]);

export const childrenMap: ICurdComponentMap<IComponentType> = new Map<
  IComponentType,
  ICurdComponentMapValue
>([
  ["select", markRaw(ElOption)],
  ["radio", markRaw(ElRadio)],
  ["checkbox", markRaw(ElCheckbox)],
]);
