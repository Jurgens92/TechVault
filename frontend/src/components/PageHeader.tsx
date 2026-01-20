import React from 'react';
import { Button } from './ui/Button';
import { Input } from './ui/Input';
import { LucideIcon, Search } from 'lucide-react';

interface PageHeaderProps {
  // Title and subtitle
  title: string;
  subtitle?: string;

  // Optional icon badge (for Dashboard/Settings style)
  icon?: LucideIcon;

  // Optional action button
  actionButton?: {
    label: string;
    icon?: LucideIcon;
    onClick: () => void;
    className?: string;
  };

  // Optional search functionality
  search?: {
    placeholder?: string;
    onSearch: (query: string) => void;
    className?: string;
  };

  // Custom content slot (for tabs, filters, etc.)
  children?: React.ReactNode;

  // Custom className for the container
  className?: string;
}

export const PageHeader: React.FC<PageHeaderProps> = ({
  title,
  subtitle,
  icon: Icon,
  actionButton,
  search,
  children,
  className = '',
}) => {
  const [searchQuery, setSearchQuery] = React.useState('');

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
    search?.onSearch(e.target.value);
  };

  return (
    <div className={`mb-8 space-y-4 ${className}`}>
      {/* Header row with icon, title, and action button */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          {Icon && (
            <div className="bg-primary/10 p-3 rounded-xl border border-primary/20">
              <Icon className="h-8 w-8 text-primary" />
            </div>
          )}
          <div>
            <h1 className="text-3xl font-bold">{title}</h1>
            {subtitle && (
              <p className="text-muted-foreground mt-1">{subtitle}</p>
            )}
          </div>
        </div>

        {actionButton && (
          <Button
            onClick={actionButton.onClick}
            className={actionButton.className || 'flex items-center gap-2 bg-blue-600 hover:bg-blue-700'}
          >
            {actionButton.icon && <actionButton.icon className="w-4 h-4" />}
            {actionButton.label}
          </Button>
        )}
      </div>

      {/* Search bar */}
      {search && (
        <div className="relative">
          <Search className="absolute left-3 top-3 w-4 h-4 text-muted-foreground" />
          <Input
            type="text"
            placeholder={search.placeholder || 'Search...'}
            value={searchQuery}
            onChange={handleSearchChange}
            className={search.className || 'pl-10 bg-secondary border-border text-foreground placeholder:text-muted-foreground'}
          />
        </div>
      )}

      {/* Custom content slot */}
      {children}
    </div>
  );
};
