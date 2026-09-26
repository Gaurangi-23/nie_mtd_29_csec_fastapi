import { Routes, Route, Navigate, Link, useNavigate } from 'react-router-dom';

import Login from './Login';
import Register from './Register';
import TicketList from './TicketList';
import TicketForm from './TicketForm';

import './App.css';


function ProtectedRoute({ children }) {

    const token = localStorage.getItem('token');

    return token ? children : <Navigate to="/login" />;
}


function Navigation() {

    const navigate = useNavigate();

    const token = localStorage.getItem('token');

    const logout = () => {

        localStorage.removeItem('token');
        localStorage.removeItem('username');
        localStorage.removeItem('role');

        navigate('/login');
    };

    if (!token) {
        return null;
    }

    return (
        <nav className="navbar navbar-expand-lg navbar-dark bg-dark">
            <div className="container">

                <Link className="navbar-brand" to="/tickets">
                    E-Commerce Support
                </Link>

                <div className="d-flex align-items-center">

                    <Link
                        className="btn btn-outline-light me-2"
                        to="/tickets"
                    >
                        Tickets
                    </Link>

                    <Link
                        className="btn btn-success me-2"
                        to="/tickets/new"
                    >
                        Create Ticket
                    </Link>

                    <button
                        className="btn btn-danger"
                        onClick={logout}
                    >
                        Logout
                    </button>

                </div>

            </div>
        </nav>
    );
}


function App() {

    return (
        <>
            <Navigation />

            <Routes>

                <Route
                    path="/"
                    element={<Navigate to="/tickets" />}
                />

                <Route
                    path="/login"
                    element={<Login />}
                />

                <Route
                    path="/register"
                    element={<Register />}
                />

                <Route
                    path="/tickets"
                    element={
                        <ProtectedRoute>
                            <TicketList />
                        </ProtectedRoute>
                    }
                />

                <Route
                    path="/tickets/new"
                    element={
                        <ProtectedRoute>
                            <TicketForm />
                        </ProtectedRoute>
                    }
                />

                <Route
                    path="/tickets/edit/:id"
                    element={
                        <ProtectedRoute>
                            <TicketForm />
                        </ProtectedRoute>
                    }
                />

                <Route
                    path="*"
                    element={<Navigate to="/tickets" />}
                />

            </Routes>
        </>
    );
}

export default App;