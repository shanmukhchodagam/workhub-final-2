export type TaskStatus = 'upcoming' | 'ongoing' | 'completed';
export type TaskPriority = 'low' | 'normal' | 'high' | 'urgent';

export interface User {
    id: number;
    email: string;
    full_name: string;
    role: 'Manager' | 'Employee';
    team_id: number;
    username?: string; // for backward compatibility
}

export interface Employee {
    id: number;
    email: string;
    full_name: string;
    role: 'Employee';
    team_id: number;
    avatar?: string;
}

export interface Task {
    id: number;
    title: string;
    description: string;
    status: TaskStatus;
    priority: TaskPriority;
    assigned_to: number[];
    assigned_users?: Employee[];
    assigned_by: number;
    team_id: number;
    due_date?: string;
    location?: string;
    created_at: string;
    updated_at: string;
    estimated_hours?: number;
    tags?: string[];
}

export interface TaskColumn {
    id: string;
    title: string;
    status: TaskStatus;
    tasks: Task[];
}

export interface CreateTaskRequest {
    title: string;
    description: string;
    status: TaskStatus;
    priority: TaskPriority;
    assigned_to: number[];
    due_date?: string;
    location?: string;
    estimated_hours?: number;
    tags?: string[];
}

export interface UpdateTaskRequest extends Partial<CreateTaskRequest> {
    id: number;
}

export interface Incident {
    id: number;
    description: string;
    severity: 'low' | 'medium' | 'high';
    reported_by: number;
    image_url?: string;
    created_at: string;
}

export interface Message {
    id?: number;
    content: string;
    sender_id: number;
    intent?: string;
    created_at?: string;
    type?: 'message' | 'agent_response';
}
