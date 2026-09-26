import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

import api from './api';


function TicketList() {

    const navigate = useNavigate();

    const [tickets, setTickets] = useState([]);

    const [category, setCategory] = useState('');
    const [status, setStatus] = useState('');

    const [error, setError] = useState('');
    const [loading, setLoading] = useState(true);


    const role = Number(
        localStorage.getItem('role')
    );


    const getTickets = async () => {

        setLoading(true);
        setError('');

        try {

            let response;

            if (category) {

                response = await api.get(
                    `/tickets/category/${encodeURIComponent(category)}`
                );

            } else if (status) {

                response = await api.get(
                    `/tickets/status/${encodeURIComponent(status)}`
                );

            } else {

                response = await api.get('/tickets');
            }

            setTickets(response.data);

        } catch (error) {

            if (error.response) {

                setError(
                    error.response.data.detail ||
                    'Unable to fetch tickets'
                );

            } else {

                setError(
                    'Unable to connect to the server'
                );
            }

            setTickets([]);

        } finally {

            setLoading(false);
        }
    };


    useEffect(() => {

        getTickets();

    }, [category, status]);


    const clearFilters = () => {

        setCategory('');
        setStatus('');
    };


    const deleteTicket = async (id) => {

        const confirmDelete = window.confirm(
            'Are you sure you want to delete this ticket?'
        );

        if (!confirmDelete) {
            return;
        }

        try {

            await api.delete(`/tickets/${id}`);

            getTickets();

        } catch (error) {

            setError(
                error.response?.data?.detail ||
                'Unable to delete ticket'
            );
        }
    };


    const editTicket = (id) => {

        navigate(`/tickets/edit/${id}`);
    };


    return (
        <div className="container mt-5">

            <div className="d-flex justify-content-between align-items-center mb-4">

                <div>

                    <h2>
                        Support Tickets
                    </h2>

                    <p className="text-muted mb-0">
                        Logged in as: {
                            localStorage.getItem('username')
                        } | Role: {role}
                    </p>

                </div>

                <Link
                    to="/tickets/new"
                    className="btn btn-primary"
                >
                    + Create Ticket
                </Link>

            </div>


            {error && (
                <div className="alert alert-danger">
                    {error}
                </div>
            )}


            <div className="card mb-4">

                <div className="card-body">

                    <div className="row">

                        <div className="col-md-5">

                            <label className="form-label">
                                Category
                            </label>

                            <select
                                className="form-select"
                                value={category}
                                onChange={(e) => {
                                    setCategory(e.target.value);
                                    setStatus('');
                                }}
                            >

                                <option value="">
                                    All Categories
                                </option>

                                <option value="ORDER_NOT_RECEIVED">
                                    Order Not Received
                                </option>

                                <option value="WRONG_ITEM">
                                    Wrong Item
                                </option>

                                <option value="DAMAGED_ITEM">
                                    Damaged Item
                                </option>

                                <option value="CANCEL_ORDER">
                                    Cancel Order
                                </option>

                                <option value="REFUND">
                                    Refund
                                </option>

                                <option value="RETURN">
                                    Return
                                </option>

                                <option value="PAYMENT_ISSUE">
                                    Payment Issue
                                </option>

                            </select>

                        </div>


                        <div className="col-md-5">

                            <label className="form-label">
                                Status
                            </label>

                            <select
                                className="form-select"
                                value={status}
                                onChange={(e) => {
                                    setStatus(e.target.value);
                                    setCategory('');
                                }}
                            >

                                <option value="">
                                    All Statuses
                                </option>

                                <option value="NEW">
                                    NEW
                                </option>

                                <option value="ASSIGNED">
                                    ASSIGNED
                                </option>

                                <option value="IN_PROGRESS">
                                    IN PROGRESS
                                </option>

                                <option value="RESOLVED">
                                    RESOLVED
                                </option>

                                <option value="CLOSED">
                                    CLOSED
                                </option>

                            </select>

                        </div>


                        <div className="col-md-2 d-flex align-items-end">

                            <button
                                className="btn btn-secondary w-100"
                                onClick={clearFilters}
                            >
                                Clear
                            </button>

                        </div>

                    </div>

                </div>

            </div>


            {loading ? (

                <div className="text-center">
                    <div className="spinner-border"></div>
                </div>

            ) : tickets.length === 0 ? (

                <div className="alert alert-info">
                    No tickets found.
                </div>

            ) : (

                <div className="table-responsive">

                    <table className="table table-bordered table-hover">

                        <thead className="table-dark">

                            <tr>

                                <th>ID</th>
                                <th>Title</th>
                                <th>Description</th>
                                <th>Category</th>
                                <th>Status</th>
                                <th>Actions</th>

                            </tr>

                        </thead>


                        <tbody>

                            {tickets.map((ticket) => (

                                <tr key={ticket.id}>

                                    <td>
                                        <small>
                                            {ticket.id}
                                        </small>
                                    </td>

                                    <td>
                                        {ticket.title}
                                    </td>

                                    <td>
                                        {ticket.description}
                                    </td>

                                    <td>
                                        {ticket.category}
                                    </td>

                                    <td>
                                        <span className="badge bg-primary">
                                            {ticket.status}
                                        </span>
                                    </td>

                                    <td>

                                        {(role === 2 ||
                                            role === 3 ||
                                            role === 4) && (

                                            <button
                                                className="btn btn-warning btn-sm me-2"
                                                onClick={() =>
                                                    editTicket(ticket.id)
                                                }
                                            >
                                                Edit
                                            </button>

                                        )}


                                        {role === 4 && (

                                            <button
                                                className="btn btn-danger btn-sm"
                                                onClick={() =>
                                                    deleteTicket(ticket.id)
                                                }
                                            >
                                                Delete
                                            </button>

                                        )}

                                    </td>

                                </tr>

                            ))}

                        </tbody>

                    </table>

                </div>

            )}

        </div>
    );
}

export default TicketList;