// User and Authentication Types
export interface User {
    id: number;
    email: string;
    first_name: string;
    last_name: string;
    role: 'citizen' | 'admin';
    address?: string;
    city?: string;
    phone_number?: string;
    profile?: UserProfile;
    date_joined?: string;
    last_login?: string;
  }
  
  export interface UserProfile {
    email_notifications: boolean;
    push_notifications: boolean;
    default_view: string;
    notification_threshold: number;
  }
  
  export interface AuthState {
    user: User | null;
    accessToken: string | null;
    refreshToken: string | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    error: string | null;
  }
  
  export interface LoginCredentials {
    email: string;
    password: string;
  }
  
  export interface RegistrationData {
    email: string;
    password: string;
    password2: string;
    first_name: string;
    last_name: string;
    role?: 'citizen' | 'admin';
    address?: string;
    city?: string;
    phone_number?: string;
  }
  
  export interface AuthResponse {
    user: User;
    access: string;
    refresh: string;
  }
  
  export interface PasswordChangeData {
    old_password: string;
    new_password: string;
    new_password2: string;
  }
  
  export interface PasswordResetRequestData {
    email: string;
  }
  
  export interface PasswordResetConfirmData {
    uid: string;
    token: string;
    new_password: string;
    new_password2: string;
  }
  
  // Environmental Data Types
  export interface EnvironmentalMeasurement {
    id: number;
    timestamp: string;
    location: string;
    latitude: number;
    longitude: number;
    pm25?: number;
    pm10?: number;
    o3?: number;
    no2?: number;
    so2?: number;
    co?: number;
    temperature?: number;
    humidity?: number;
    wind_speed?: number;
    wind_direction?: number;
    pressure?: number;
    precipitation?: number;
    traffic_volume?: number;
    traffic_speed?: number;
    data_source: string;
  }
  
  export interface Prediction {
    id: number;
    timestamp: string;
    target_time: string;
    location: string;
    latitude: number;
    longitude: number;
    predicted_pm25?: number;
    predicted_pm10?: number;
    predicted_o3?: number;
    predicted_no2?: number;
    predicted_traffic?: number;
    model_name: string;
    model_version: string;
    confidence?: number;
  }
  
  export interface Alert {
    id: number;
    timestamp: string;
    location: string;
    alert_type: 'pollution' | 'weather' | 'traffic';
    severity: 'low' | 'medium' | 'high' | 'critical';
    title: string;
    description: string;
    is_active: boolean;
    resolved_at?: string;
    measurement?: number;
    prediction?: number;
  }
  
  export interface UserAlert {
    id: number;
    user: number;
    alert: Alert;
    is_read: boolean;
    read_at?: string;
  }
  
  export interface DashboardData {
    latest_measurements: EnvironmentalMeasurement[];
    predictions: Prediction[];
    active_alerts: Alert[];
    user_alerts: UserAlert[];
  }
  
  // Filter and query types
  export interface MeasurementFilters {
    location?: string;
    start_date?: string;
    end_date?: string;
    source?: string;
  }
  
  export interface PredictionFilters {
    location?: string;
    start_date?: string;
    end_date?: string;
    model?: string;
  }
  
  export interface AlertFilters {
    location?: string;
    type?: 'pollution' | 'weather' | 'traffic';
    severity?: 'low' | 'medium' | 'high' | 'critical';
    active?: boolean;
  }
  
  // Pagination
  export interface PaginatedResponse<T> {
    count: number;
    next: string | null;
    previous: string | null;
    results: T[];
  }