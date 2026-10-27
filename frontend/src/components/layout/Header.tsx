import React from "react";
import { Wind, HelpCircle, FileText } from "lucide-react";
import { Button } from "../ui/button";

interface HeaderProps {
  onOpenAssumptions: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onOpenAssumptions }) => {
  return (
    <header className="sticky top-0 z-40 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        <div className="flex items-center space-x-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
            <Wind className="h-6 w-6 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-bold tracking-tight md:text-xl">
                UK Wind Forecast Decision Dashboard
              </h1>
              <span className="rounded-full bg-primary/10 px-2 py-0.5 text-xs font-semibold text-primary">
                Pilot
              </span>
            </div>
            <p className="text-xs text-muted-foreground hidden sm:block">
              Day-Ahead Power Buying Decision Support · January 2026 · Elexon BMRS
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={onOpenAssumptions}
            className="flex items-center gap-1.5"
          >
            <HelpCircle className="h-4 w-4" />
            <span className="hidden sm:inline">Assumptions & Rules</span>
          </Button>
          <a
            href="/docs"
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center"
          >
            <Button variant="ghost" size="sm" className="flex items-center gap-1.5">
              <FileText className="h-4 w-4" />
              <span className="hidden sm:inline">API Docs</span>
            </Button>
          </a>
        </div>
      </div>
    </header>
  );
};
