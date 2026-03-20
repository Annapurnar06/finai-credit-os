import Sidebar from "./Sidebar";
import TopBar from "./TopBar";

interface AppShellProps {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
}

export default function AppShell({ title, subtitle, children }: AppShellProps) {
  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <div className="flex flex-col flex-1 min-w-0">
        <TopBar title={title} subtitle={subtitle} />
        <main className="flex-1 overflow-auto">{children}</main>
      </div>
    </div>
  );
}
