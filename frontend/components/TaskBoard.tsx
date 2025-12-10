'use client';

import React, { useState, useEffect } from 'react';
import {
  DndContext,
  DragEndEvent,
  DragOverEvent,
  DragOverlay,
  DragStartEvent,
  PointerSensor,
  useSensor,
  useSensors,
  closestCorners,
} from '@dnd-kit/core';
import {
  SortableContext,
  arrayMove,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import {
  useSortable,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { 
  Plus, 
  Calendar, 
  MapPin, 
  Clock, 
  User,
  AlertTriangle,
  CheckCircle2,
  Timer,
  Users
} from 'lucide-react';
import { Task, TaskColumn, Employee } from '@/types';
import { cn } from '@/lib/utils';
import { TaskDetailsModal } from './TaskDetailsModal';

interface TaskCardProps {
  task: Task;
  isOverlay?: boolean;
  onClick?: (task: Task) => void;
}

function TaskCard({ task, isOverlay = false, onClick }: TaskCardProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({
    id: task.id,
  });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'bg-red-500';
      case 'high': return 'bg-orange-500';
      case 'normal': return 'bg-blue-500';
      case 'low': return 'bg-gray-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'upcoming': return <Timer className="h-4 w-4" />;
      case 'ongoing': return <AlertTriangle className="h-4 w-4" />;
      case 'completed': return <CheckCircle2 className="h-4 w-4" />;
      default: return <Timer className="h-4 w-4" />;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    });
  };

  const getInitials = (name: string) => {
    return name.split(' ').map(n => n[0]).join('').toUpperCase();
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
      className={cn(
        'cursor-grab active:cursor-grabbing',
        isDragging && 'opacity-50',
        isOverlay && 'rotate-5 shadow-xl'
      )}
    >
      <Card className="mb-3 hover:shadow-md transition-shadow bg-white border-l-4 cursor-pointer" 
            onClick={(e) => {
              e.stopPropagation();
              onClick?.(task);
            }}
            style={{ borderLeftColor: task.priority === 'urgent' ? '#ef4444' : 
                                      task.priority === 'high' ? '#f97316' :
                                      task.priority === 'normal' ? '#3b82f6' : '#6b7280' }}>
        <CardContent className="p-4">
          {/* Priority indicator and assignees */}
          <div className="flex justify-between items-start mb-2">
            <Badge 
              variant="secondary" 
              className={cn("text-white text-xs", getPriorityColor(task.priority))}
            >
              {task.priority.toUpperCase()}
            </Badge>
            
            {/* Assignee avatars */}
            <div className="flex -space-x-2">
              {task.assigned_users?.slice(0, 3).map((user, index) => (
                <Avatar key={user.id} className="h-6 w-6 border-2 border-white">
                  <AvatarImage src={user.avatar} alt={user.full_name} />
                  <AvatarFallback className="text-xs bg-blue-500 text-white">
                    {getInitials(user.full_name)}
                  </AvatarFallback>
                </Avatar>
              ))}
              {task.assigned_users && task.assigned_users.length > 3 && (
                <Avatar className="h-6 w-6 border-2 border-white">
                  <AvatarFallback className="text-xs bg-gray-500 text-white">
                    +{task.assigned_users.length - 3}
                  </AvatarFallback>
                </Avatar>
              )}
            </div>
          </div>

          {/* Task title and description */}
          <h4 className="font-semibold text-sm mb-2 text-gray-900 line-clamp-2">
            {task.title}
          </h4>
          
          {task.description && (
            <p className="text-xs text-gray-600 mb-3 line-clamp-2">
              {task.description}
            </p>
          )}

          {/* Task metadata */}
          <div className="space-y-2">
            {task.due_date && (
              <div className="flex items-center gap-1 text-xs text-gray-500">
                <Calendar className="h-3 w-3" />
                <span>Due {formatDate(task.due_date)}</span>
              </div>
            )}
            
            {task.location && (
              <div className="flex items-center gap-1 text-xs text-gray-500">
                <MapPin className="h-3 w-3" />
                <span className="truncate">{task.location}</span>
              </div>
            )}
            
            {task.estimated_hours && (
              <div className="flex items-center gap-1 text-xs text-gray-500">
                <Clock className="h-3 w-3" />
                <span>{task.estimated_hours}h estimated</span>
              </div>
            )}
          </div>

          {/* Tags */}
          {task.tags && task.tags.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {task.tags.slice(0, 2).map((tag, index) => (
                <Badge key={index} variant="outline" className="text-xs px-1 py-0">
                  {tag}
                </Badge>
              ))}
              {task.tags.length > 2 && (
                <Badge variant="outline" className="text-xs px-1 py-0">
                  +{task.tags.length - 2}
                </Badge>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

interface TaskColumnProps {
  column: TaskColumn;
  tasks: Task[];
  onAddTask: (status: string) => void;
  onTaskClick: (task: Task) => void;
}

function TaskColumnComponent({ column, tasks, onAddTask, onTaskClick }: TaskColumnProps) {
  const {
    setNodeRef,
  } = useSortable({
    id: column.id,
  });

  const getColumnIcon = (status: string) => {
    switch (status) {
      case 'upcoming': return <Timer className="h-5 w-5 text-blue-500" />;
      case 'ongoing': return <AlertTriangle className="h-5 w-5 text-orange-500" />;
      case 'completed': return <CheckCircle2 className="h-5 w-5 text-green-500" />;
      default: return <Timer className="h-5 w-5" />;
    }
  };

  const getColumnColor = (status: string) => {
    switch (status) {
      case 'upcoming': return 'border-blue-200 bg-blue-50/30';
      case 'ongoing': return 'border-orange-200 bg-orange-50/30';
      case 'completed': return 'border-green-200 bg-green-50/30';
      default: return 'border-gray-200 bg-gray-50/30';
    }
  };

  return (
    <div className={cn("flex-1 min-w-[300px] max-w-[400px]")}>
      <Card className={cn("h-full", getColumnColor(column.status))}>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              {getColumnIcon(column.status)}
              <CardTitle className="text-lg font-semibold">
                {column.title}
              </CardTitle>
              <Badge variant="secondary" className="text-xs">
                {tasks.length}
              </Badge>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onAddTask(column.status)}
              className="h-8 w-8 p-0 hover:bg-white/80"
            >
              <Plus className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent className="pt-0 pb-4">
          <div
            ref={setNodeRef}
            className="min-h-[500px] space-y-2"
          >
            <SortableContext
              items={tasks.map(task => task.id)}
              strategy={verticalListSortingStrategy}
            >
              {tasks.map((task) => (
                <TaskCard key={task.id} task={task} onClick={onTaskClick} />
              ))}
            </SortableContext>
            
            {tasks.length === 0 && (
              <div className="flex flex-col items-center justify-center py-12 text-gray-400">
                <div className="mb-2">
                  {getColumnIcon(column.status)}
                </div>
                <p className="text-sm">No tasks yet</p>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => onAddTask(column.status)}
                  className="mt-2 text-xs"
                >
                  Add a task
                </Button>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

interface TaskBoardProps {
  tasks: Task[];
  employees: Employee[];
  onTaskUpdate: (taskId: number, updates: Partial<Task>) => Promise<void>;
  onAddTask: (status: string) => void;
}

export function TaskBoard({ tasks, employees, onTaskUpdate, onAddTask }: TaskBoardProps) {
  const [activeTask, setActiveTask] = useState<Task | null>(null);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [columns, setColumns] = useState<TaskColumn[]>([
    { id: 'upcoming', title: 'Upcoming', status: 'upcoming', tasks: [] },
    { id: 'ongoing', title: 'Ongoing', status: 'ongoing', tasks: [] },
    { id: 'completed', title: 'Completed', status: 'completed', tasks: [] },
  ]);

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    })
  );

  // Update columns when tasks change
  useEffect(() => {
    const updatedColumns = columns.map(column => ({
      ...column,
      tasks: tasks.filter(task => task.status === column.status)
        .map(task => ({
          ...task,
          assigned_users: task.assigned_to.map(userId => 
            employees.find(emp => emp.id === userId)
          ).filter(Boolean) as Employee[]
        }))
    }));
    setColumns(updatedColumns);
  }, [tasks, employees]);

  function handleDragStart(event: DragStartEvent) {
    const { active } = event;
    const task = tasks.find(t => t.id === active.id);
    setActiveTask(task || null);
  }

  function handleDragEnd(event: DragEndEvent) {
    const { active, over } = event;
    setActiveTask(null);

    if (!over) return;

    const activeTask = tasks.find(t => t.id === active.id);
    if (!activeTask) return;

    // Check if dropped on a different column
    const overColumn = columns.find(col => 
      col.id === over.id || 
      col.tasks.some(task => task.id === over.id)
    );

    if (!overColumn) return;

    // Update task status if moved to different column
    if (activeTask.status !== overColumn.status) {
      onTaskUpdate(activeTask.id, { status: overColumn.status });
    }

    // Handle reordering within the same column
    const activeColumn = columns.find(col => col.status === activeTask.status);
    if (activeColumn && overColumn.id === activeColumn.id) {
      const oldIndex = activeColumn.tasks.findIndex(t => t.id === active.id);
      const newIndex = activeColumn.tasks.findIndex(t => t.id === over.id);
      
      if (oldIndex !== newIndex) {
        const newTasks = arrayMove(activeColumn.tasks, oldIndex, newIndex);
        // Here you could implement task order persistence if needed
      }
    }
  }

  const handleTaskClick = (task: Task) => {
    setSelectedTask(task);
    setIsModalOpen(true);
  };

  const handleTaskUpdate = (updatedTask: Task) => {
    onTaskUpdate(updatedTask.id, updatedTask);
    setIsModalOpen(false);
    setSelectedTask(null);
  };

  return (
    <div className="w-full">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Task Management</h2>
        <p className="text-gray-600">Drag and drop tasks between columns to update their status</p>
      </div>

      <DndContext
        sensors={sensors}
        collisionDetection={closestCorners}
        onDragStart={handleDragStart}
        onDragEnd={handleDragEnd}
      >
        <div className="flex gap-6 overflow-x-auto pb-4">
          {columns.map((column) => (
            <TaskColumnComponent
              key={column.id}
              column={column}
              tasks={column.tasks}
              onAddTask={onAddTask}
              onTaskClick={handleTaskClick}
            />
          ))}
        </div>

        <DragOverlay>
          {activeTask ? <TaskCard task={activeTask} isOverlay /> : null}
        </DragOverlay>
      </DndContext>

      <TaskDetailsModal
        task={selectedTask}
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setSelectedTask(null);
        }}
        onTaskUpdate={handleTaskUpdate}
        employees={employees}
      />
    </div>
  );
}