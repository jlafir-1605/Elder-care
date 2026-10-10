
import axios from 'axios'

const api = axios.create({
  baseURL: 'https://eldercare-backend-y085.onrender.com/api',
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const register = (payload) => api.post('/auth/register', payload)
export const login = (payload) => api.post('/auth/login', payload)

export const getDashboard = () => api.get('/dashboard')
export const getBookings = () => api.get('/bookings')
export const createBooking = (payload) => api.post('/bookings', payload)
export const updateBookingStatus = (bookingId, status) =>
  api.patch(`/bookings/${bookingId}/status`, { status })
export const completeBooking = (bookingId) =>
  api.post(`/bookings/${bookingId}/complete`)

export const getMyCharges = () => api.get('/charges')
export const getRecruiterCharges = (recruiterId) =>
  api.get(`/charges/recruiter/${recruiterId}`)
export const createCharges = (payload) => api.post('/charges', payload)
export const updateCharges = (payload) => api.put('/charges', payload)

export const createReview = (payload) => api.post('/reviews', payload)
export const getRecruiterReviews = (recruiterId) =>
  api.get(`/reviews/recruiter/${recruiterId}`)
export const getReviewSummary = (recruiterId) =>
  api.get(`/reviews/recruiter/${recruiterId}/summary`)
export const canReviewBooking = (bookingId) =>
  api.get(`/reviews/booking/${bookingId}/can-review`)

export const submitVerification = (payload) =>
  api.post('/verification', payload)
export const getRecruiterVerification = (recruiterId) =>
  api.get(`/verification/recruiter/${recruiterId}`)
export const approveVerification = (verificationId) =>
  api.patch(`/verification/${verificationId}/approve`)
export const rejectVerification = (verificationId) =>
  api.patch(`/verification/${verificationId}/reject`)

export default api
