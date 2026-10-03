"use client";

import { useAuthStore } from "@/store/authStore";
import { useRouter, usePathname } from "next/navigation";
import { useEffect } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { FileText, MessageSquare, LogOut, LayoutDashboard } from "lucide-react";
import { cn } from "@/utils/cn";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { user, isAuthenticated, logout } = useAuthStore();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login");
    }
  }, [isAuthenticated, router]);

  if (!isAuthenticated) return null;

  const navItems = [
    { name: "Documents", href: "/dashboard", icon: LayoutDashboard },
    { name: "Chat", href: "/dashboard/chat", icon: MessageSquare },
  ];

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 flex selection:bg-indigo-500/30">
      {/* Sidebar */}
      <aside className="w-64 border-r border-zinc-800/50 bg-zinc-900/20 backdrop-blur-xl flex flex-col fixed inset-y-0 z-50">
        <div className="p-6">
          <div className="flex items-center gap-3 text-indigo-400 font-bold text-xl">
            <FileText className="w-6 h-6" />
            SmartDoc
          </div>
        </div>

        <nav className="flex-1 px-4 space-y-2 mt-4">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;
            return (
              <Link key={item.name} href={item.href}>
                <span
                  className={cn(
                    "flex items-center gap-3 px-4 py-3 rounded-xl transition-all font-medium text-sm relative group overflow-hidden",
                    isActive
                      ? "text-white bg-indigo-500/10"
                      : "text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800/50"
                  )}
                >
                  {isActive && (
                    <motion.div
                      layoutId="activeTab"
                      className="absolute inset-0 bg-indigo-500/10 border border-indigo-500/20 rounded-xl"
                      transition={{ type: "spring", stiffness: 300, damping: 30 }}
                    />
                  )}
                  <Icon className="w-5 h-5 relative z-10" />
                  <span className="relative z-10">{item.name}</span>
                </span>
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t border-zinc-800/50">
          <div className="px-4 py-3 bg-zinc-900/50 rounded-xl mb-2 flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-cyan-500 flex items-center justify-center text-sm font-bold shadow-lg">
              {user?.username?.[0]?.toUpperCase()}
            </div>
            <div className="flex-1 overflow-hidden">
              <p className="text-sm font-medium truncate">{user?.username}</p>
              <p className="text-xs text-zinc-500 truncate">{user?.email}</p>
            </div>
          </div>
          <button
            onClick={() => {
              logout();
              router.push("/login");
            }}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-zinc-400 hover:text-red-400 hover:bg-red-400/10 transition-colors text-sm font-medium"
          >
            <LogOut className="w-5 h-5" />
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 pl-64">
        <div className="p-8 max-w-6xl mx-auto h-full">
          {children}
        </div>
      </main>
    </div>
  );
}
