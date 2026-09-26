import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

import api from './api';


function Login() {

    const navigate = useNavigate();

    const [form, setForm] = useState({
        username: '',
        password: ''
    });

    const [error, setError] = useState('');

    const [loading, setLoading] = useState(false);


    const handleChange = (e) => {

        setForm({
            ...form,
            [e.target.name]: e.target.value
        });
    };


    const login = async (e) => {

        e.preventDefault();

        setError('');
        setLoading(true);

        const data = new URLSearchParams();

        data.append('username', form.username);
        data.append('password', form.password);

        try {

            const response = await api.post(
                '/login',
                data,
                {
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    }
                }
            );

            localStorage.setItem(
                'token',
                response.data.access_token
            );

            /*
             * Your current /login response only contains:
             *
             * access_token
             * token_type
             *
             * It does NOT return username or role.
             *
             * We decode the JWT payload here to get them.
             */

            const token = response.data.access_token;

            const payload = JSON.parse(
                atob(token.split('.')[1])
            );

            localStorage.setItem(
                'username',
                payload.sub
            );

            localStorage.setItem(
                'role',
                payload.role
            );

            navigate('/tickets');

        } catch (error) {

            if (error.response) {

                setError(
                    error.response.data.detail ||
                    'Invalid username or password'
                );

            } else {

                setError(
                    'Unable to connect to the server'
                );
            }

        } finally {

            setLoading(false);
        }
    };


    return (
        <div className="container login-container">

            <div className="row justify-content-center">

                <div className="col-md-5">

                    <div className="card shadow">

                        <div className="card-body">

                            <h2 className="text-center mb-4">
                                Login
                            </h2>

                            {error && (
                                <div className="alert alert-danger">
                                    {error}
                                </div>
                            )}

                            <form onSubmit={login}>

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


                                <button
                                    type="submit"
                                    className="btn btn-primary w-100"
                                    disabled={loading}
                                >
                                    {loading ? 'Logging in...' : 'Login'}
                                </button>

                            </form>


                            <div className="text-center mt-3">

                                <span>
                                    Don't have an account?{' '}
                                </span>

                                <Link to="/register">
                                    Register
                                </Link>

                            </div>

                        </div>

                    </div>

                </div>

            </div>

        </div>
    );
}

export default Login;