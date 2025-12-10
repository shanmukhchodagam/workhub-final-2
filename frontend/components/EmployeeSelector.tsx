'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Employee } from '@/types';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { X, Search, User } from 'lucide-react';
import { cn } from '@/lib/utils';

interface EmployeeSelectorProps {
  employees: Employee[];
  selectedEmployees: Employee[];
  onEmployeeSelect: (employee: Employee) => void;
  onEmployeeRemove: (employeeId: number) => void;
  placeholder?: string;
  className?: string;
  maxSelections?: number;
}

export function EmployeeSelector({
  employees,
  selectedEmployees,
  onEmployeeSelect,
  onEmployeeRemove,
  placeholder = "Search and assign employees...",
  className,
  maxSelections
}: EmployeeSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const getInitials = (name: string) => {
    return name.split(' ').map(n => n[0]).join('').toUpperCase();
  };

  // Filter employees based on search term and exclude already selected
  const filteredEmployees = employees.filter(employee => {
    const matchesSearch = employee.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         employee.email.toLowerCase().includes(searchTerm.toLowerCase());
    const notSelected = !selectedEmployees.find(selected => selected.id === employee.id);
    return matchesSearch && notSelected;
  });

  // Handle keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isOpen) {
      if (e.key === 'Enter' || e.key === 'ArrowDown') {
        setIsOpen(true);
        setHighlightedIndex(0);
        e.preventDefault();
      }
      return;
    }

    switch (e.key) {
      case 'ArrowDown':
        setHighlightedIndex(prev => 
          prev < filteredEmployees.length - 1 ? prev + 1 : 0
        );
        e.preventDefault();
        break;
      case 'ArrowUp':
        setHighlightedIndex(prev => 
          prev > 0 ? prev - 1 : filteredEmployees.length - 1
        );
        e.preventDefault();
        break;
      case 'Enter':
        if (highlightedIndex >= 0 && highlightedIndex < filteredEmployees.length) {
          handleEmployeeSelect(filteredEmployees[highlightedIndex]);
        }
        e.preventDefault();
        break;
      case 'Escape':
        setIsOpen(false);
        setHighlightedIndex(-1);
        inputRef.current?.blur();
        break;
    }
  };

  const handleEmployeeSelect = (employee: Employee) => {
    if (maxSelections && selectedEmployees.length >= maxSelections) {
      return;
    }
    onEmployeeSelect(employee);
    setSearchTerm('');
    setHighlightedIndex(-1);
    setIsOpen(false);
    inputRef.current?.focus();
  };

  const handleEmployeeRemove = (employeeId: number) => {
    onEmployeeRemove(employeeId);
    inputRef.current?.focus();
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className={cn("relative", className)} ref={dropdownRef}>
      {/* Selected Employees */}
      {selectedEmployees.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-2">
          {selectedEmployees.map((employee) => (
            <Badge 
              key={employee.id} 
              variant="secondary"
              className="flex items-center gap-2 px-2 py-1 bg-blue-50 text-blue-700 border border-blue-200"
            >
              <Avatar className="h-5 w-5">
                <AvatarImage src={employee.avatar} alt={employee.full_name} />
                <AvatarFallback className="text-xs bg-blue-500 text-white">
                  {getInitials(employee.full_name)}
                </AvatarFallback>
              </Avatar>
              <span className="text-sm font-medium">{employee.full_name}</span>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => handleEmployeeRemove(employee.id)}
                className="h-4 w-4 p-0 hover:bg-blue-100 rounded-full"
              >
                <X className="h-3 w-3" />
              </Button>
            </Badge>
          ))}
        </div>
      )}

      {/* Search Input */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
        <Input
          ref={inputRef}
          type="text"
          placeholder={maxSelections && selectedEmployees.length >= maxSelections 
            ? `Maximum ${maxSelections} employees selected` 
            : placeholder
          }
          value={searchTerm}
          onChange={(e) => {
            setSearchTerm(e.target.value);
            setIsOpen(true);
            setHighlightedIndex(0);
          }}
          onFocus={() => setIsOpen(true)}
          onKeyDown={handleKeyDown}
          className="pl-10"
          disabled={Boolean(maxSelections && selectedEmployees.length >= maxSelections)}
        />
      </div>

      {/* Dropdown */}
      {isOpen && (
        <div className="absolute top-full left-0 right-0 z-50 mt-1 bg-white border border-gray-200 rounded-md shadow-lg max-h-60 overflow-y-auto">
          {filteredEmployees.length > 0 ? (
            <ul className="py-1">
              {filteredEmployees.map((employee, index) => (
                <li key={employee.id}>
                  <button
                    className={cn(
                      "w-full text-left px-3 py-2 hover:bg-gray-50 flex items-center gap-3 transition-colors",
                      index === highlightedIndex && "bg-blue-50 text-blue-700"
                    )}
                    onClick={() => handleEmployeeSelect(employee)}
                    onMouseEnter={() => setHighlightedIndex(index)}
                  >
                    <Avatar className="h-8 w-8">
                      <AvatarImage src={employee.avatar} alt={employee.full_name} />
                      <AvatarFallback className="bg-gray-500 text-white text-xs">
                        {getInitials(employee.full_name)}
                      </AvatarFallback>
                    </Avatar>
                    <div className="flex-1">
                      <div className="font-medium text-sm">{employee.full_name}</div>
                      <div className="text-xs text-gray-500">{employee.email}</div>
                    </div>
                    <Badge variant="outline" className="text-xs">
                      {employee.role}
                    </Badge>
                  </button>
                </li>
              ))}
            </ul>
          ) : (
            <div className="px-3 py-4 text-center text-gray-500">
              {searchTerm ? (
                <div>
                  <User className="h-8 w-8 mx-auto mb-2 text-gray-300" />
                  <p className="text-sm">No employees found matching "{searchTerm}"</p>
                </div>
              ) : (
                <div>
                  <User className="h-8 w-8 mx-auto mb-2 text-gray-300" />
                  <p className="text-sm">No more employees to assign</p>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}