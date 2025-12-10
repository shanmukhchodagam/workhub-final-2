'use client';

import React, { useState } from 'react';
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogFooter, 
  DialogHeader, 
  DialogTitle 
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from '@/components/ui/select';
import { EmployeeSelector } from '@/components/EmployeeSelector';
import { 
  CalendarDays, 
  MapPin, 
  Clock, 
  AlertTriangle, 
  CheckCircle2, 
  Timer,
  Tag,
  X
} from 'lucide-react';
import { Employee, CreateTaskRequest } from '@/types';
import { cn } from '@/lib/utils';

interface CreateTaskModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreateTask: (task: CreateTaskRequest) => Promise<void>;
  employees: Employee[];
  initialStatus?: 'upcoming' | 'ongoing' | 'completed';
}

const PRIORITY_OPTIONS = [
  { value: 'low', label: 'Low Priority', color: 'bg-gray-500', icon: Timer },
  { value: 'normal', label: 'Normal Priority', color: 'bg-blue-500', icon: Timer },
  { value: 'high', label: 'High Priority', color: 'bg-orange-500', icon: AlertTriangle },
  { value: 'urgent', label: 'Urgent', color: 'bg-red-500', icon: AlertTriangle },
];

const STATUS_OPTIONS = [
  { value: 'upcoming', label: 'Upcoming', icon: Timer },
  { value: 'ongoing', label: 'Ongoing', icon: AlertTriangle },
  { value: 'completed', label: 'Completed', icon: CheckCircle2 },
];

const PREDEFINED_TAGS = [
  'Installation', 'Maintenance', 'Repair', 'Inspection', 'Emergency', 
  'Training', 'Documentation', 'Safety Check', 'Equipment', 'Software'
];

export function CreateTaskModal({ 
  isOpen, 
  onClose, 
  onCreateTask, 
  employees, 
  initialStatus = 'upcoming' 
}: CreateTaskModalProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [selectedEmployees, setSelectedEmployees] = useState<Employee[]>([]);
  const [customTags, setCustomTags] = useState<string[]>([]);
  const [newTag, setNewTag] = useState('');
  
  const [formData, setFormData] = useState<Omit<CreateTaskRequest, 'assigned_to'>>({
    title: '',
    description: '',
    status: initialStatus,
    priority: 'normal',
    due_date: '',
    location: '',
    estimated_hours: undefined,
    tags: [],
  });

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleEmployeeSelect = (employee: Employee) => {
    if (!selectedEmployees.find(emp => emp.id === employee.id)) {
      setSelectedEmployees(prev => [...prev, employee]);
    }
  };

  const handleEmployeeRemove = (employeeId: number) => {
    setSelectedEmployees(prev => prev.filter(emp => emp.id !== employeeId));
  };

  const handleAddTag = (tag: string) => {
    const trimmedTag = tag.trim();
    if (trimmedTag && !customTags.includes(trimmedTag)) {
      setCustomTags(prev => [...prev, trimmedTag]);
      setNewTag('');
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setCustomTags(prev => prev.filter(tag => tag !== tagToRemove));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.title.trim()) {
      return;
    }

    if (selectedEmployees.length === 0) {
      return;
    }

    setIsLoading(true);

    try {
      const taskData: CreateTaskRequest = {
        title: formData.title,
        description: formData.description || "",
        status: formData.status,
        priority: formData.priority,
        assigned_to: selectedEmployees.map(emp => emp.id),
        due_date: formData.due_date || undefined, // Handle empty date
        location: formData.location || undefined, // Handle empty location
        estimated_hours: formData.estimated_hours || undefined,
        tags: customTags.length > 0 ? customTags : undefined,
      };

      await onCreateTask(taskData);
      
      // Reset form
      setFormData({
        title: '',
        description: '',
        status: initialStatus,
        priority: 'normal',
        due_date: '',
        location: '',
        estimated_hours: undefined,
        tags: [],
      });
      setSelectedEmployees([]);
      setCustomTags([]);
      setNewTag('');
      
      onClose();
    } catch (error) {
      console.error('Failed to create task:', error);
      // Handle error (show toast, etc.)
    } finally {
      setIsLoading(false);
    }
  };

  const getPriorityOption = (priority: string) => {
    return PRIORITY_OPTIONS.find(option => option.value === priority) || PRIORITY_OPTIONS[1];
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Timer className="h-5 w-5" />
            Create New Task
          </DialogTitle>
          <DialogDescription>
            Create and assign a new task to your team members. Fill in the details below.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Task Title */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700">
              Task Title *
            </label>
            <Input
              placeholder="Enter task title..."
              value={formData.title}
              onChange={(e) => handleInputChange('title', e.target.value)}
              className="w-full"
              required
            />
          </div>

          {/* Task Description */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700">
              Description
            </label>
            <Textarea
              placeholder="Describe the task, requirements, and any important details..."
              value={formData.description}
              onChange={(e) => handleInputChange('description', e.target.value)}
              className="w-full min-h-[100px]"
            />
          </div>

          {/* Employee Assignment */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700">
              Assign To *
            </label>
            <EmployeeSelector
              employees={employees}
              selectedEmployees={selectedEmployees}
              onEmployeeSelect={handleEmployeeSelect}
              onEmployeeRemove={handleEmployeeRemove}
              placeholder="Search and assign employees to this task..."
            />
          </div>

          {/* Status and Priority Row */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">Status</label>
              <Select
                value={formData.status}
                onValueChange={(value: 'upcoming' | 'ongoing' | 'completed') => 
                  handleInputChange('status', value)
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select status" />
                </SelectTrigger>
                <SelectContent>
                  {STATUS_OPTIONS.map((status) => {
                    const Icon = status.icon;
                    return (
                      <SelectItem key={status.value} value={status.value}>
                        <div className="flex items-center gap-2">
                          <Icon className="h-4 w-4" />
                          {status.label}
                        </div>
                      </SelectItem>
                    );
                  })}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">Priority</label>
              <Select
                value={formData.priority}
                onValueChange={(value: 'low' | 'normal' | 'high' | 'urgent') => 
                  handleInputChange('priority', value)
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select priority" />
                </SelectTrigger>
                <SelectContent>
                  {PRIORITY_OPTIONS.map((priority) => {
                    const Icon = priority.icon;
                    return (
                      <SelectItem key={priority.value} value={priority.value}>
                        <div className="flex items-center gap-2">
                          <div className={cn("w-3 h-3 rounded-full", priority.color)} />
                          <Icon className="h-4 w-4" />
                          {priority.label}
                        </div>
                      </SelectItem>
                    );
                  })}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Due Date and Location */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">
                <CalendarDays className="h-4 w-4 inline mr-1" />
                Due Date
              </label>
              <Input
                type="datetime-local"
                value={formData.due_date}
                onChange={(e) => handleInputChange('due_date', e.target.value)}
                className="w-full"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">
                <MapPin className="h-4 w-4 inline mr-1" />
                Location
              </label>
              <Input
                placeholder="e.g., Building A, Site 1, Office..."
                value={formData.location}
                onChange={(e) => handleInputChange('location', e.target.value)}
                className="w-full"
              />
            </div>
          </div>

          {/* Estimated Hours */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700">
              <Clock className="h-4 w-4 inline mr-1" />
              Estimated Hours
            </label>
            <Input
              type="number"
              min="0.5"
              step="0.5"
              placeholder="e.g., 2.5"
              value={formData.estimated_hours || ''}
              onChange={(e) => handleInputChange('estimated_hours', 
                e.target.value ? parseFloat(e.target.value) : undefined
              )}
              className="w-full"
            />
          </div>

          {/* Tags */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700">
              <Tag className="h-4 w-4 inline mr-1" />
              Tags
            </label>
            
            {/* Predefined Tags */}
            <div className="flex flex-wrap gap-2 mb-2">
              {PREDEFINED_TAGS.map((tag) => (
                <Badge
                  key={tag}
                  variant={customTags.includes(tag) ? "default" : "outline"}
                  className="cursor-pointer"
                  onClick={() => 
                    customTags.includes(tag) 
                      ? handleRemoveTag(tag)
                      : handleAddTag(tag)
                  }
                >
                  {tag}
                </Badge>
              ))}
            </div>

            {/* Custom Tag Input */}
            <div className="flex gap-2">
              <Input
                placeholder="Add custom tag..."
                value={newTag}
                onChange={(e) => setNewTag(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    handleAddTag(newTag);
                  }
                }}
                className="flex-1"
              />
              <Button
                type="button"
                variant="outline"
                onClick={() => handleAddTag(newTag)}
                disabled={!newTag.trim()}
              >
                Add
              </Button>
            </div>

            {/* Selected Custom Tags */}
            {customTags.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {customTags.map((tag) => (
                  <Badge key={tag} variant="default" className="flex items-center gap-1">
                    {tag}
                    <X 
                      className="h-3 w-3 cursor-pointer" 
                      onClick={() => handleRemoveTag(tag)}
                    />
                  </Badge>
                ))}
              </div>
            )}
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button 
              type="submit" 
              disabled={isLoading || !formData.title.trim() || selectedEmployees.length === 0}
            >
              {isLoading ? 'Creating...' : 'Create Task'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}