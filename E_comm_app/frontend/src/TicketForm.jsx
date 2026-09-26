import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

import api from './api';


function TicketForm() {

    const navigate = useNavigate();

    const { id } = useParams();

    const isEdit = Boolean(id);


    const [form, setForm] = useState({
        title: '',
        description: '',
        category: '',
        status: 'NEW'
    });


    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);


    const handleChange = (e) => {

        setForm({
            ...form,
            [e.target.name]: e.target.value
        });
    };


    useEffect(() => {

        if (isEdit) {

            getTicket();

        }

    }, [id]);


    const getTicket = async () => {

        try {

            const response = await api.get(
                `/tickets/${id}`
            );

            setForm({
                title: response.data.title,
                description: response.data.description,
                category: response.data.category,
                status: response.data.status
            });

        } catch (error) {

            setError(
                error.response?.data?.detail ||
                'Unable to fetch ticket'
            );
        }
    };


    const saveTicket = async (e) => {

        e.preventDefault();

        setError('');
        setLoading(true);

        try {

            if (isEdit) {

                await api.put(
                    `/tickets/${id}`,
                    form
                );

            } else {

                await api.post(
                    '/tickets',
                    form
                );
            }

            navigate('/tickets');

        } catch (error) {

            setError(
                error.response?.data?.detail ||
                'Unable to save ticket'
            );

        } finally {

            setLoading(false);
        }
    };


    return (
        <div className="container mt-5">

            <div className="row justify-content-center">

                <div className="col-md-8">

                    <div className="card shadow">

                        <div className="card-body">

                            <h2 className="mb-4">

                                {isEdit
                                    ? 'Edit Ticket'
                                    : 'Create Ticket'
                                }

                            </h2>


                            {error && (

                                <div className="alert alert-danger">
                                    {error}
                                </div>

                            )}


                            <form onSubmit={saveTicket}>

                                <div className="mb-3">

                                    <label className="form-label">
                                        Title
                                    </label>

                                    <input
                                        type="text"
                                        name="title"
                                        className="form-control"
                                        value={form.title}
                                        onChange={handleChange}
                                        required
                                    />

                                </div>


                                <div className="mb-3">

                                    <label className="form-label">
                                        Description
                                    </label>

                                    <textarea
                                        name="description"
                                        className="form-control"
                                        rows="5"
                                        value={form.description}
                                        onChange={handleChange}
                                        required
                                    />

                                </div>


                                <div className="mb-3">

                                    <label className="form-label">
                                        Category
                                    </label>

                                    <select
                                        name="category"
                                        className="form-select"
                                        value={form.category}
                                        onChange={handleChange}
                                        required
                                    >

                                        <option value="">
                                            Select Category
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


                                <div className="mb-3">

                                    <label className="form-label">
                                        Status
                                    </label>

                                    <select
                                        name="status"
                                        className="form-select"
                                        value={form.status}
                                        onChange={handleChange}
                                        required
                                    >

                                        <option value="NEW">
                                            NEW
                                        </option>

                                        <option value="ASSIGNED">
                                            ASSIGNED
                                        </option>

                                        <option value="IN_PROGRESS">
                                            IN_PROGRESS
                                        </option>

                                        <option value="RESOLVED">
                                            RESOLVED
                                        </option>

                                        <option value="CLOSED">
                                            CLOSED
                                        </option>

                                    </select>

                                </div>


                                <div className="d-flex gap-2">

                                    <button
                                        type="submit"
                                        className="btn btn-success"
                                        disabled={loading}
                                    >
                                        {loading
                                            ? 'Saving...'
                                            : isEdit
                                                ? 'Update Ticket'
                                                : 'Create Ticket'
                                        }
                                    </button>


                                    <button
                                        type="button"
                                        className="btn btn-secondary"
                                        onClick={() =>
                                            navigate('/tickets')
                                        }
                                    >
                                        Cancel
                                    </button>

                                </div>

                            </form>

                        </div>

                    </div>

                </div>

            </div>

        </div>
    );
}

export default TicketForm;