import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

import api from './api';


function Register() {

    const navigate = useNavigate();

    const [form, setForm] = useState({
        username: '',
        password: '',
        role: 1
    });

    const [error, setError] = useState('');
    const [message, setMessage] = useState('');


    const handleChange = (e) => {

        setForm({
            ...form,
            [e.target.name]: e.target.value
        });
    };


    const register = async (e) => {

        e.preventDefault();

        setError('');
        setMessage('');

        try {

            await api.post('/users', {
                username: form.username,
                password: form.password,
                role: Number(form.role)
            });

            setMessage(
                'Registration successful. You can now login.'
            );

            setTimeout(() => {
                navigate('/login');
            }, 1500);

        } catch (error) {

            if (error.response) {

                setError(
                    error.response.data.detail ||
                    'Registration failed'
                );

            } else {

                setError(
                    'Unable to connect to the server'
                );
            }
        }
    };


    return (
        <div className="container login-container">

            <div className="row justify-content-center">

                <div className="col-md-5">

                    <div className="card shadow">

                        <div className="card-body">

                            <h2 className="text-center mb-4">
                                Register
                            </h2>

                            {error && (
                                <div className="alert alert-danger">
                                    {error}
                                </div>
                            )}

                            {message && (
                                <div className="alert alert-success">
                                    {message}
                                </div>
                            )}


                            <form onSubmit={register}>

                                <div className="mb-3">

                                    <label className="form-label">
                                        Username
                                    </label>

                                    <input
                                        type="text"
                                        name="username"
                                        className="form-control"
                                        value={form.username}
                                        onChange={handleChange}
                                        required
                                    />

                                </div>


                                <div className="mb-3">

                                    <label className="form-label">
                                        Password
                                    </label>

                                    <input
                                        type="password"
                                        name="password"
                                        className="form-control"
                                        value={form.password}
                                        onChange={handleChange}
                                        required
                                    />

                                </div>


                                <div className="mb-3">

                                    <label className="form-label">
                                        Role
                                    </label>

                                    <select
                                        name="role"
                                        className="form-select"
                                        value={form.role}
                                        onChange={handleChange}
                                    >

                                        <option value="1">
                                            Role 1
                                        </option>

                                        <option value="2">
                                            Role 2
                                        </option>

                                        <option value="3">
                                            Role 3
                                        </option>

                                        <option value="4">
                                            Role 4
                                        </option>

                                    </select>

                                </div>


                                <button
                                    type="submit"
                                    className="btn btn-success w-100"
                                >
                                    Register
                                </button>

                            </form>


                            <div className="text-center mt-3">

                                <span>
                                    Already have an account?{' '}
                                </span>

                                <Link to="/login">
                                    Login
                                </Link>

                            </div>

                        </div>

                    </div>

                </div>

            </div>

        </div>
    );
}

export default Register;