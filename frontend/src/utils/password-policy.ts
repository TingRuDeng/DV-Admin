import type { PasswordPolicy } from "@/api/information-api";

export function passwordLengthError(
  value: string,
  policy: PasswordPolicy | null
): string | undefined {
  if (
    !policy ||
    !Number.isInteger(policy.minLength) ||
    !Number.isInteger(policy.maxLength) ||
    policy.minLength < 15 ||
    policy.maxLength > 128 ||
    policy.minLength > policy.maxLength
  ) {
    return "密码规则尚未加载，请重试";
  }
  const length = Array.from(value).length;
  if (length < policy.minLength || length > policy.maxLength) {
    return `密码长度必须为 ${policy.minLength}-${policy.maxLength} 个字符`;
  }
}
