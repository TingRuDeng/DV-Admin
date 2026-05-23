export const enum ProfileDialogType {
  ACCOUNT = "account",
  PASSWORD = "password",
}

export interface ProfileDialogState {
  visible: boolean;
  title: string;
  type: ProfileDialogType | "";
}
