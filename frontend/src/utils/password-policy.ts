import type { PasswordPolicy } from "@/api/information-api";

export interface PasswordErrorMessages {
  policyUnavailable: string;
  invalidLength: (min: number, max: number) => string;
}

const DEFAULT_MESSAGES: PasswordErrorMessages = {
  policyUnavailable: "密码规则尚未加载，请重试",
  invalidLength: (min, max) => `密码长度必须为 ${min}-${max} 个字符`,
};

export function passwordLengthError(
  value: string,
  policy: PasswordPolicy | null,
  messages: PasswordErrorMessages = DEFAULT_MESSAGES
): string | undefined {
  if (
    !policy ||
    !Number.isInteger(policy.minLength) ||
    !Number.isInteger(policy.maxLength) ||
    policy.minLength < 15 ||
    policy.maxLength > 128 ||
    policy.minLength > policy.maxLength
  ) {
    return messages.policyUnavailable;
  }
  const length = Array.from(value).length;
  if (length < policy.minLength || length > policy.maxLength) {
    return messages.invalidLength(policy.minLength, policy.maxLength);
  }
}
