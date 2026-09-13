export const enum ProfileDialogType {
  ACCOUNT = "account",
  PASSWORD = "password",
}

export interface ProfileDialogState {
  visible: boolean;
  titleKey: "profile.accountDialog" | "profile.passwordDialog" | "";
  type: ProfileDialogType | "";
}
