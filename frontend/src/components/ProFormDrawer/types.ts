import type { Ref } from "vue";
import type { FormInstance } from "element-plus";

export interface ProFormDrawerExpose {
  formRef: Ref<FormInstance | undefined>;
  resetFields: () => void;
  clearValidate: () => void;
  validate: (
    callback?: Parameters<FormInstance["validate"]>[0]
  ) => ReturnType<FormInstance["validate"]> | undefined;
}
