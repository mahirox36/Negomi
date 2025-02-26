export interface User {
  id: string;
  username: string;
  avatar: string;
  global_name?: string;
}

export interface Guild {
  id: string;
  name: string;
  icon: string | null;
  owner: boolean;
  permissions: string;
}
