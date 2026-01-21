import React from 'react';
import { Card } from './ui/Card';
import { Building2 } from 'lucide-react';

interface EmptyOrgStateProps {
  message?: string;
}

export const EmptyOrgState: React.FC<EmptyOrgStateProps> = ({
  message = 'Please select an organization from the sidebar to view this content.'
}) => {
  return (
    <Card className="p-12 text-center">
      <Building2 className="w-16 h-16 text-gray-500 mx-auto mb-4" />
      <h3 className="text-lg font-semibold text-foreground mb-2">No Organization Selected</h3>
      <p className="text-muted-foreground">{message}</p>
    </Card>
  );
};
