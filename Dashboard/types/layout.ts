export interface SidebarItem {
  name: string;
  icon: string;
}

export interface SidebarLayout {
  [section: string]: SidebarItem[];
}

export interface LayoutItem {
  type: "header" | "cards" | "panel";
  text?: string;
  subtext?: string;
  icon?: string;
  interaction?: string;
  buttons?: Array<{
    text: string;
    subtext: string;
    icon: string;
    link: string;
    buttonText: string;
  }>;
  settings?: Array<{
    name: string;
    type: string;
    value: string;
    description?: string;
  }>;
}
