type LoginDefaultEnv = Partial<
  Pick<ImportMetaEnv, "VITE_LOGIN_DEFAULT_USERNAME" | "VITE_LOGIN_DEFAULT_PASSWORD">
>;

export function getLoginDefaultCredentials(env: LoginDefaultEnv = import.meta.env) {
  return {
    username: env.VITE_LOGIN_DEFAULT_USERNAME || "",
    password: env.VITE_LOGIN_DEFAULT_PASSWORD || "",
  };
}
