"use client";

import React, { useState, useEffect } from 'react';
import { X, Edit, Save, Calendar, MapPin, Clock, AlertCircle, Users } from 'lucide-react';
import { Task, Employee, TaskPriority, TaskStatus } from '../types';
import { EmployeeSelector } from './EmployeeSelector';
import { updateTask } from '../lib/api';

interface TaskDetailsModalProps {
  task: Task | null;
  isOpen: boolean;
  onClose: () => void;
  onTaskUpdate: (updatedTask: Task) => void;
  employees: Employee[];
}

export function TaskDetailsModal({ 
  task, 
  isOpen, 
  onClose, 
  onTaskUpdate, 
  employees 
}: TaskDetailsModalProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editedTask, setEditedTask] = useState<Task | null>(null);
  const [loading, setLoading] = useState(false);

  // Reset state when task changes
  useEffect(() => {
    if (task) {
      setEditedTask({ ...task });
      setIsEditing(false);
    }
  }, [task]);

  const handleSave = async () => {
    if (!editedTask) return;

    setLoading(true);
    try {
      const updatedTask = await updateTask(editedTask.id, {
        title: editedTask.title,
        description: editedTask.description,
        assigned_to: editedTask.assigned_to,
        status: editedTask.status,
        priority: editedTask.priority,
        due_date: editedTask.due_date,
        location: editedTask.location,
        estimated_hours: editedTask.estimated_hours,
      });
      
      onTaskUpdate(updatedTask);
      setIsEditing(false);
    } catch (error) {
      console.error('Failed to update task:', error);
      alert('Failed to update task. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    if (task) {
      setEditedTask({ ...task });
    }
    setIsEditing(false);
  };

  const formatDate = (dateString: string | null | undefined) => {
    if (!dateString) return 'Not set';
    return new Date(dateString).toLocaleDateString();
  };

  const getSelectedEmployeeObjects = () => {
    if (!editedTask?.assigned_to) return [];
    return employees.filter(emp => editedTask.assigned_to.includes(emp.id));
  };

  const handleEmployeeSelect = (employee: Employee) => {
    if (!editedTask) return;
    const currentIds = editedTask.assigned_to || [];
    if (!currentIds.includes(employee.id)) {
      setEditedTask({ ...editedTask, assigned_to: [...currentIds, employee.id] });
    }
  };

  const handleEmployeeRemove = (employeeId: number) => {
    if (!editedTask) return;
    const currentIds = editedTask.assigned_to || [];
    setEditedTask({ 
      ...editedTask, 
      assigned_to: currentIds.filter(id => id !== employeeId) 
    });
  };

  const getAssignedEmployees = () => {
    if (!task?.assigned_to) return [];
    return employees.filter(emp => task.assigned_to.includes(emp.id));
  };

  const getPriorityColor = (priority: TaskPriority) => {
    switch (priority) {
      case 'urgent': return 'text-red-600 bg-red-50';
      case 'high': return 'text-orange-600 bg-orange-50';
      case 'normal': return 'text-blue-600 bg-blue-50';
      case 'low': return 'text-gray-600 bg-gray-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getStatusColor = (status: TaskStatus) => {
    switch (status) {
      case 'upcoming': return 'text-blue-600 bg-blue-50';
      case 'ongoing': return 'text-yellow-600 bg-yellow-50';
      case 'completed': return 'text-green-600 bg-green-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  if (!isOpen || !task || !editedTask) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full m-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-900">
            {isEditing ? 'Edit Task' : 'Task Details'}
          </h2>
          <div className="flex items-center gap-2">
            {!isEditing ? (
              <button
                onClick={() => setIsEditing(true)}
                className="p-2 text-gray-500 hover:text-gray-700 rounded-lg hover:bg-gray-100"
              >
                <Edit className="h-5 w-5" />
              </button>
            ) : (
              <>
                <button
                  onClick={handleSave}
                  disabled={loading}
                  className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 disabled:opacity-50"
                >
                  {loading ? 'Saving...' : 'Save'}
                </button>
                <button
                  onClick={handleCancel}
                  className="px-3 py-1 bg-gray-300 text-gray-700 rounded text-sm hover:bg-gray-400"
                >
                  Cancel
                </button>
              </>
            )}
            <button
              onClick={onClose}
              className="p-2 text-gray-500 hover:text-gray-700 rounded-lg hover:bg-gray-100"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Title */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Task Title
            </label>
            {isEditing ? (
              <input
                type="text"
                value={editedTask.title}
                onChange={(e) => setEditedTask({ ...editedTask, title: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter task title"
              />
            ) : (
              <h3 className="text-lg font-medium text-gray-900">{task.title}</h3>
            )}
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description
            </label>
            {isEditing ? (
              <textarea
                value={editedTask.description || ''}
                onChange={(e) => setEditedTask({ ...editedTask, description: e.target.value })}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter task description"
              />
            ) : (
              <p className="text-gray-700">
                {task.description || 'No description provided'}
              </p>
            )}
          </div>

          {/* Status and Priority */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Status
              </label>
              {isEditing ? (
                <select
                  value={editedTask.status}
                  onChange={(e) => setEditedTask({ ...editedTask, status: e.target.value as TaskStatus })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="upcoming">Upcoming</option>
                  <option value="ongoing">Ongoing</option>
                  <option value="completed">Completed</option>
                </select>
              ) : (
                <span className={`inline-flex px-2 py-1 rounded-full text-xs font-medium capitalize ${getStatusColor(task.status)}`}>
                  {task.status}
                </span>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Priority
              </label>
              {isEditing ? (
                <select
                  value={editedTask.priority}
                  onChange={(e) => setEditedTask({ ...editedTask, priority: e.target.value as TaskPriority })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="low">Low</option>
                  <option value="normal">Normal</option>
                  <option value="high">High</option>
                  <option value="urgent">Urgent</option>
                </select>
              ) : (
                <span className={`inline-flex px-2 py-1 rounded-full text-xs font-medium capitalize ${getPriorityColor(task.priority)}`}>
                  {task.priority}
                </span>
              )}
            </div>
          </div>

          {/* Assigned Employees */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Users className="inline h-4 w-4 mr-1" />
              Assigned To
            </label>
            {isEditing ? (
              <EmployeeSelector
                employees={employees}
                selectedEmployees={getSelectedEmployeeObjects()}
                onEmployeeSelect={handleEmployeeSelect}
                onEmployeeRemove={handleEmployeeRemove}
                placeholder="Select employees..."
              />
            ) : (
              <div className="flex flex-wrap gap-2">
                {getAssignedEmployees().length > 0 ? (
                  getAssignedEmployees().map((employee) => (
                    <div
                      key={employee.id}
                      className="flex items-center gap-2 px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-sm"
                    >
                      <div className="h-6 w-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs">
                        {employee.full_name.charAt(0).toUpperCase()}
                      </div>
                      {employee.full_name}
                    </div>
                  ))
                ) : (
                  <span className="text-gray-500">No one assigned</span>
                )}
              </div>
            )}
          </div>

          {/* Due Date */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Calendar className="inline h-4 w-4 mr-1" />
              Due Date
            </label>
            {isEditing ? (
              <input
                type="datetime-local"
                value={editedTask.due_date ? new Date(editedTask.due_date).toISOString().slice(0, 16) : ''}
                onChange={(e) => setEditedTask({ 
                  ...editedTask, 
                  due_date: e.target.value ? new Date(e.target.value).toISOString() : undefined 
                })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            ) : (
              <p className="text-gray-700">{formatDate(task.due_date)}</p>
            )}
          </div>

          {/* Location */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <MapPin className="inline h-4 w-4 mr-1" />
              Location
            </label>
            {isEditing ? (
              <input
                type="text"
                value={editedTask.location || ''}
                onChange={(e) => setEditedTask({ ...editedTask, location: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter location"
              />
            ) : (
              <p className="text-gray-700">{task.location || 'No location specified'}</p>
            )}
          </div>

          {/* Estimated Hours */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Clock className="inline h-4 w-4 mr-1" />
              Estimated Hours
            </label>
            {isEditing ? (
              <input
                type="number"
                step="0.5"
                min="0"
                value={editedTask.estimated_hours || ''}
                onChange={(e) => setEditedTask({ 
                  ...editedTask, 
                  estimated_hours: e.target.value ? parseFloat(e.target.value) : undefined 
                })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter estimated hours"
              />
            ) : (
              <p className="text-gray-700">
                {task.estimated_hours ? `${task.estimated_hours} hours` : 'Not specified'}
              </p>
            )}
          </div>

          {/* Timestamps */}
          <div className="border-t pt-4 text-sm text-gray-500">
            <p>Created: {formatDate(task.created_at)}</p>
            {task.updated_at && task.updated_at !== task.created_at && (
              <p>Last updated: {formatDate(task.updated_at)}</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}