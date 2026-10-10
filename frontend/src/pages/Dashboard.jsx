import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  completeBooking,
  createBooking,
  getBookings,
  getDashboard,
  getMyCharges,
  updateBookingStatus,
  updateCharges,
} from '../api'
import { useAuth } from '../auth/AuthContext'

const ROLE_RECRUITER = 1
const CARE_TYPES = [
  { value: 'hourly', label: 'Hourly care' },
  { value: 'daily', label: 'Daily care' },
  { value: 'live_in', label: 'Live-in care' },
  { value: 'medical', label: 'Medical care' },
  { value: 'companionship', label: 'Companionship' },
  { value: 'personal_care', label: 'Personal care' },
  { value: 'other', label: 'Other' },
]
const TIME_SLOTS = ['08:00 AM', '10:00 AM', '12:00 PM', '02:00 PM', '04:00 PM', '06:00 PM']
const STATUS_LABELS = {
  pending: 'Pending',
  accepted: 'Accepted',
  rejected: 'Rejected',
  completed: 'Completed',
  cancelled: 'Cancelled',
}

function valueOrFallback(value) {
  return value || 'Not provided'
}

function formatBookingDate(value) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

function statusClass(status) {
  return `status-badge status-${String(status || 'pending').toLowerCase()}`
}

function formatCharge(value) {
  if (value === null || value === undefined || value === '') return 'Not set'
  const numericValue = Number(value)
  return Number.isFinite(numericValue)
    ? numericValue.toLocaleString(undefined, { maximumFractionDigits: 2 })
    : String(value)
}

function chargesToForm(charges) {
  return {
    hourlyCharge: charges?.hourly_charge ?? '',
    dailyCharge: charges?.daily_charge ?? '',
    serviceCharges: charges?.service_charges ?? '',
  }
}

function parseOptionalNumber(value) {
  const trimmedValue = String(value ?? '').trim()
  if (!trimmedValue) return null
  const numericValue = Number(trimmedValue)
  return Number.isFinite(numericValue) && numericValue >= 0 ? numericValue : undefined
}

function ChargesDisplay({ charges, compact = false }) {
  const hourlyCharge = charges?.hourly_charge
  const dailyCharge = charges?.daily_charge
  const serviceCharges = charges?.service_charges
  const hasCharges = hourlyCharge !== null && hourlyCharge !== undefined && hourlyCharge !== ''
    || dailyCharge !== null && dailyCharge !== undefined && dailyCharge !== ''
    || Boolean(serviceCharges?.trim())

  return (
    <div className={`charges-display${compact ? ' compact' : ''}`}>
      <p className="charges-title">Service charges</p>
      {hasCharges ? (
        <dl className="charges-grid">
          {hourlyCharge !== null && hourlyCharge !== undefined && hourlyCharge !== '' && (
            <div><dt>Hourly</dt><dd>{formatCharge(hourlyCharge)}</dd></div>
          )}
          {dailyCharge !== null && dailyCharge !== undefined && dailyCharge !== '' && (
            <div><dt>Daily</dt><dd>{formatCharge(dailyCharge)}</dd></div>
          )}
          {serviceCharges?.trim() && (
            <div className="charges-service"><dt>Service-specific</dt><dd>{serviceCharges.trim()}</dd></div>
          )}
        </dl>
      ) : (
        <p className="charges-empty">No charges set</p>
      )}
    </div>
  )
}

function ChargesPanel({ charges, form, setForm, onSave, loading, saving, error }) {
  function updateForm(field, value) {
    setForm((current) => ({ ...current, [field]: value }))
  }

  return (
      <div className="charges-panel">
      {charges && <ChargesDisplay charges={charges} compact />}
      {loading ? (
        <div className="dashboard-state">Loading your charges...</div>
      ) : (
        <form onSubmit={onSave}>
          {error && <div className="alert error">{error}</div>}
          <div className="charges-form-grid">
            <div className="form-field">
              <label htmlFor="hourlyCharge">Hourly charge</label>
              <input
                id="hourlyCharge"
                type="number"
                min="0"
                step="0.01"
                value={form.hourlyCharge}
                onChange={(event) => updateForm('hourlyCharge', event.target.value)}
                placeholder="Enter hourly charge"
              />
            </div>
            <div className="form-field">
              <label htmlFor="dailyCharge">Daily charge</label>
              <input
                id="dailyCharge"
                type="number"
                min="0"
                step="0.01"
                value={form.dailyCharge}
                onChange={(event) => updateForm('dailyCharge', event.target.value)}
                placeholder="Enter daily charge"
              />
            </div>
            <div className="form-field charges-service-field">
              <label htmlFor="serviceCharges">Service-specific charges <span className="optional-label">(optional)</span></label>
              <textarea
                id="serviceCharges"
                value={form.serviceCharges}
                onChange={(event) => updateForm('serviceCharges', event.target.value)}
                placeholder="Describe service-specific charges"
                maxLength={1000}
                rows={4}
              />
            </div>
          </div>
          <div className="charges-actions">
            <button className="action-button accept-button" type="submit" disabled={saving}>
              {saving ? 'Saving…' : 'Save charges'}
            </button>
          </div>
        </form>
      )}
    </div>
  )
}

function ProfileCard({ profile, label, onBook }) {
  return (
    <article className="profile-card">
      <div className="profile-heading">
        <div className="avatar">{profile.full_name?.charAt(0).toUpperCase()}</div>
        <div>
          <p className="eyebrow">{label}</p>
          <h3>{profile.full_name}</h3>
        </div>
      </div>
      <dl className="details-grid">
        <div><dt>Email</dt><dd>{profile.email}</dd></div>
        <div><dt>Phone</dt><dd>{valueOrFallback(profile.phone)}</dd></div>
        <div><dt>Address</dt><dd>{valueOrFallback(profile.address)}</dd></div>
        <div><dt>City</dt><dd>{valueOrFallback(profile.city)}</dd></div>
        <div><dt>State</dt><dd>{valueOrFallback(profile.state)}</dd></div>
        <div><dt>Age</dt><dd>{valueOrFallback(profile.age)}</dd></div>
        {profile.emergency_contact && (
          <div><dt>Emergency Contact</dt><dd>{profile.emergency_contact}</dd></div>
        )}
      </dl>
      {profile.role === ROLE_RECRUITER && <ChargesDisplay charges={profile.charges} />}
      {onBook && (
        <button className="book-button" type="button" onClick={() => onBook(profile)}>
          Book Recruiter
        </button>
      )}
    </article>
  )
}

function BookingCard({ booking, isRecruiter, onStatus, onComplete, actionLoading }) {
  const status = String(booking.status || 'pending').toLowerCase()
  const otherPartyName = isRecruiter ? booking.customer_name : booking.recruiter_name
  const otherPartyEmail = isRecruiter ? booking.customer_email : booking.recruiter_email
  const otherPartyPhone = isRecruiter ? booking.customer_phone : booking.recruiter_phone
  const otherPartyAddress = isRecruiter ? booking.customer_address : booking.recruiter_address
  const otherPartyCity = isRecruiter ? booking.customer_city : booking.recruiter_city
  const otherPartyState = isRecruiter ? booking.customer_state : booking.recruiter_state
  const otherPartyAge = isRecruiter ? booking.customer_age : booking.recruiter_age

  return (
    <article className="booking-card">
      <div className="booking-card-header">
        <div>
          <p className="eyebrow">{isRecruiter ? 'Booking request' : 'Your booking'}</p>
          <h3>{otherPartyName || 'Unnamed contact'}</h3>
        </div>
        <span className={statusClass(status)}>{STATUS_LABELS[status] || booking.status}</span>
      </div>
      <dl className="booking-details">
        <div><dt>Date</dt><dd>{formatBookingDate(booking.booking_date)}</dd></div>
        <div><dt>Preferred time</dt><dd>{booking.preferred_time}</dd></div>
        <div><dt>Care type</dt><dd>{booking.care_type.replaceAll('_', ' ')}</dd></div>
        <div><dt>Contact</dt><dd>{otherPartyPhone || otherPartyEmail || 'Not provided'}</dd></div>
        {otherPartyAddress && (
          <div><dt>Address</dt><dd>{[otherPartyAddress, otherPartyCity, otherPartyState].filter(Boolean).join(', ')}</dd></div>
        )}
        {isRecruiter && otherPartyAge !== null && otherPartyAge !== undefined && (
          <div><dt>Customer age</dt><dd>{otherPartyAge}</dd></div>
        )}
        {!isRecruiter && booking.recruiter_phone && (
          <div><dt>Recruiter phone</dt><dd>{booking.recruiter_phone}</dd></div>
        )}
        {booking.message && <div className="booking-message"><dt>Requirements</dt><dd>{booking.message}</dd></div>}
      </dl>
      <div className="booking-actions">
        {isRecruiter && status === 'pending' && (
          <>
            <button
              className="action-button accept-button"
              type="button"
              disabled={actionLoading === booking.id}
              onClick={() => onStatus(booking, 'accepted')}
            >
              Accept
            </button>
            <button
              className="action-button reject-button"
              type="button"
              disabled={actionLoading === booking.id}
              onClick={() => onStatus(booking, 'rejected')}
            >
              Reject
            </button>
          </>
        )}
        {!isRecruiter && status === 'accepted' && (
          <button
            className="action-button complete-button"
            type="button"
            disabled={actionLoading === booking.id}
            onClick={() => onComplete(booking)}
          >
            Mark completed
          </button>
        )}
      </div>
    </article>
  )
}

function BookingModal({ recruiter, form, setForm, onClose, onSubmit, submitting }) {
  function updateForm(field, value) {
    setForm((current) => ({ ...current, [field]: value }))
  }

  return (
    <div className="modal-backdrop" role="presentation" onMouseDown={onClose}>
      <div
        className="booking-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="booking-modal-title"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <div className="modal-header">
          <div>
            <p className="eyebrow">New request</p>
            <h2 id="booking-modal-title">Book {recruiter.full_name}</h2>
          </div>
          <button className="modal-close" type="button" onClick={onClose} aria-label="Close booking form">×</button>
        </div>
        <ChargesDisplay charges={recruiter.charges} compact />
        <form onSubmit={onSubmit}>
          <div className="form-field">
            <label htmlFor="bookingDate">Required date</label>
            <input
              id="bookingDate"
              type="date"
              value={form.bookingDate}
              min={new Date().toISOString().slice(0, 10)}
              onChange={(event) => updateForm('bookingDate', event.target.value)}
              required
            />
          </div>
          <div className="form-field">
            <label htmlFor="preferredTime">Preferred time</label>
            <select
              id="preferredTime"
              value={form.preferredTime}
              onChange={(event) => updateForm('preferredTime', event.target.value)}
              required
            >
              <option value="">Select a time</option>
              {TIME_SLOTS.map((time) => <option key={time} value={time}>{time}</option>)}
            </select>
          </div>
          <div className="form-field">
            <label htmlFor="careType">Care or service type</label>
            <select
              id="careType"
              value={form.careType}
              onChange={(event) => updateForm('careType', event.target.value)}
              required
            >
              {CARE_TYPES.map((type) => <option key={type.value} value={type.value}>{type.label}</option>)}
            </select>
          </div>
          <div className="form-field">
            <label htmlFor="bookingMessage">Message or requirements <span className="optional-label">(optional)</span></label>
            <textarea
              id="bookingMessage"
              value={form.message}
              onChange={(event) => updateForm('message', event.target.value)}
              placeholder="Share any details the recruiter should know"
              maxLength={1000}
              rows={4}
            />
          </div>
          <div className="modal-actions">
            <button className="action-button secondary-button" type="button" onClick={onClose}>Cancel</button>
            <button className="action-button accept-button" type="submit" disabled={submitting}>
              {submitting ? 'Sending request…' : 'Confirm booking'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default function Dashboard({ role }) {
  const { user, signOut } = useAuth()
  const navigate = useNavigate()
  const [dashboard, setDashboard] = useState(null)
  const [bookings, setBookings] = useState([])
  const [charges, setCharges] = useState(null)
  const [chargeForm, setChargeForm] = useState({
    hourlyCharge: '',
    dailyCharge: '',
    serviceCharges: '',
  })
  const [error, setError] = useState('')
  const [bookingError, setBookingError] = useState('')
  const [chargesError, setChargesError] = useState('')
  const [chargesSuccess, setChargesSuccess] = useState('')
  const [loading, setLoading] = useState(true)
  const [chargesLoading, setChargesLoading] = useState(false)
  const [chargesSaving, setChargesSaving] = useState(false)
  const [bookingsLoading, setBookingsLoading] = useState(true)
  const [selectedRecruiter, setSelectedRecruiter] = useState(null)
  const [form, setForm] = useState({
    bookingDate: '',
    preferredTime: '',
    careType: 'hourly',
    message: '',
  })
  const [submitting, setSubmitting] = useState(false)
  const [actionLoading, setActionLoading] = useState(null)
  const [successMessage, setSuccessMessage] = useState('')
  const isRecruiter = role === ROLE_RECRUITER

  useEffect(() => {
    let active = true
    setLoading(true)
    setError('')
    getDashboard()
      .then(({ data }) => {
        if (active) setDashboard(data)
      })
      .catch((err) => {
        if (active) setError(err.response?.data?.detail || 'Unable to load dashboard data.')
      })
      .finally(() => {
        if (active) setLoading(false)
      })
    return () => { active = false }
  }, [])

  useEffect(() => {
    if (!isRecruiter) return undefined

    let active = true
    setChargesLoading(true)
    setChargesError('')
    getMyCharges()
      .then(({ data }) => {
        if (!active) return
        setCharges(data)
        setChargeForm(chargesToForm(data))
      })
      .catch((err) => {
        if (active) setChargesError(err.response?.data?.detail || 'Unable to load charges.')
      })
      .finally(() => {
        if (active) setChargesLoading(false)
      })

    return () => { active = false }
  }, [isRecruiter])

  useEffect(() => {
    let active = true
    setBookingsLoading(true)
    setBookingError('')
    getBookings()
      .then(({ data }) => {
        if (active) setBookings(data)
      })
      .catch((err) => {
        if (active) setBookingError(err.response?.data?.detail || 'Unable to load bookings.')
      })
      .finally(() => {
        if (active) setBookingsLoading(false)
      })
    return () => { active = false }
  }, [])

  async function refreshBookings() {
    try {
      const { data } = await getBookings()
      setBookings(data)
      setBookingError('')
    } catch (err) {
      setBookingError(err.response?.data?.detail || 'Unable to refresh bookings.')
    }
  }

  function handleSignOut() {
    signOut()
    navigate('/login', { replace: true })
  }

  function openBooking(recruiter) {
    setSelectedRecruiter(recruiter)
    setSuccessMessage('')
    setForm({ bookingDate: '', preferredTime: '', careType: 'hourly', message: '' })
  }

  function closeBookingModal() {
    setSelectedRecruiter(null)
  }

  async function handleCreateBooking(event) {
    event.preventDefault()
    setSubmitting(true)
    setSuccessMessage('')
    try {
      await createBooking({
        recruiter_id: selectedRecruiter.id,
        booking_date: `${form.bookingDate}T00:00:00`,
        preferred_time: form.preferredTime,
        care_type: form.careType,
        message: form.message.trim() || null,
      })
      closeBookingModal()
      setSuccessMessage('Booking request sent successfully.')
      await refreshBookings()
    } catch (err) {
      setBookingError(err.response?.data?.detail || 'Unable to create booking.')
    } finally {
      setSubmitting(false)
    }
  }

  async function handleBookingStatus(booking, nextStatus) {
    setActionLoading(booking.id)
    setSuccessMessage('')
    try {
      await updateBookingStatus(booking.id, nextStatus)
      setSuccessMessage(`Booking ${nextStatus} successfully.`)
      await refreshBookings()
    } catch (err) {
      setBookingError(err.response?.data?.detail || 'Unable to update booking.')
    } finally {
      setActionLoading(null)
    }
  }

  async function handleCompleteBooking(booking) {
    setActionLoading(booking.id)
    setSuccessMessage('')
    try {
      await completeBooking(booking.id)
      setSuccessMessage('Booking marked as completed.')
      await refreshBookings()
    } catch (err) {
      setBookingError(err.response?.data?.detail || 'Unable to complete booking.')
    } finally {
      setActionLoading(null)
    }
  }

  async function handleSaveCharges(event) {
    event.preventDefault()
    setChargesSaving(true)
    setChargesError('')
    setChargesSuccess('')

    const hourlyCharge = parseOptionalNumber(chargeForm.hourlyCharge)
    const dailyCharge = parseOptionalNumber(chargeForm.dailyCharge)
    if (hourlyCharge === undefined || dailyCharge === undefined) {
      setChargesError('Enter a non-negative number for each charge field.')
      setChargesSaving(false)
      return
    }

    try {
      const { data } = await updateCharges({
        hourly_charge: hourlyCharge,
        daily_charge: dailyCharge,
        service_charges: chargeForm.serviceCharges.trim() || null,
      })
      setCharges(data)
      setChargeForm(chargesToForm(data))
      setChargesSuccess('Charges updated successfully.')
    } catch (err) {
      setChargesError(err.response?.data?.detail || 'Unable to update charges.')
    } finally {
      setChargesSaving(false)
    }
  }

  const profile = dashboard?.user || user
  const contacts = dashboard?.contacts || []
  const myBookings = bookings.filter((booking) => (
    isRecruiter ? booking.recruiter_id === user?.id : booking.customer_id === user?.id
  ))
  const incomingBookings = isRecruiter ? myBookings.filter((booking) => booking.status === 'pending') : []

  return (
    <div className="dashboard-shell">
      <aside className="sidebar">
        <div className="brand-mark"><span>EC</span> ElderCare</div>
        <div className="sidebar-copy">
          <p className="eyebrow">Your workspace</p>
          <h2>{isRecruiter ? 'Care team' : 'Your care journey'}</h2>
          <p>{isRecruiter ? 'Keep track of the people looking for trusted support.' : 'Stay connected with your care team.'}</p>
        </div>
        <button className="sidebar-signout" onClick={handleSignOut}>Sign out</button>
      </aside>

      <main className="dashboard-main">
        <header className="dashboard-header">
          <div>
            <p className="eyebrow">{isRecruiter ? 'Recruiter dashboard' : 'Customer dashboard'}</p>
            <h1>Good to see you, {profile?.full_name}</h1>
          </div>
          <button className="mobile-signout ghost" onClick={handleSignOut}>Sign out</button>
        </header>

        {error && <div className="alert error">{error}</div>}
        {bookingError && <div className="alert error">{bookingError}</div>}
        {successMessage && <div className="alert success">{successMessage}</div>}
        {chargesSuccess && <div className="alert success">{chargesSuccess}</div>}
        {loading && <div className="dashboard-state">Loading your dashboard...</div>}
        {!loading && !error && dashboard && (
          <>
            <section className="summary-grid">
              <div className="summary-card accent"><span>Account type</span><strong>{isRecruiter ? 'Recruiter' : 'Customer'}</strong><small>Active member</small></div>
              <div className="summary-card"><span>{contactLabel(isRecruiter)}s available</span><strong>{contacts.length}</strong><small>From your ElderCare database</small></div>
              <div className="summary-card"><span>Booking requests</span><strong>{myBookings.length}</strong><small>{isRecruiter ? 'Incoming requests' : 'Your requests'}</small></div>
              <div className="summary-card"><span>Member since</span><strong>{new Date(profile.created_at).toLocaleDateString()}</strong><small>Account creation date</small></div>
            </section>

            {isRecruiter && (
              <section className="charges-section">
                <div className="section-heading">
                  <div><p className="eyebrow">Rates</p><h2>Manage service charges</h2></div>
                  <span className="count-pill">Visible to customers</span>
                </div>
                <ChargesPanel
                  charges={charges}
                  form={chargeForm}
                  setForm={setChargeForm}
                  onSave={handleSaveCharges}
                  loading={chargesLoading}
                  saving={chargesSaving}
                  error={chargesError}
                />
              </section>
            )}

            <section className="section-heading">
              <div><p className="eyebrow">Directory</p><h2>{isRecruiter ? 'Available customers' : 'Your recruiters'}</h2></div>
              <span className="count-pill">{contacts.length} {contactLabel(isRecruiter).toLowerCase()}{contacts.length === 1 ? '' : 's'}</span>
            </section>

            {contacts.length === 0 ? (
              <div className="empty-state"><h3>No {contactLabel(isRecruiter).toLowerCase()}s found</h3><p>There are no matching records in the ElderCare database yet.</p></div>
            ) : (
              <div className="profile-grid">
                {contacts.map((contact) => (
                  <ProfileCard
                    key={contact.id}
                    profile={contact}
                    label={contactLabel(isRecruiter)}
                    onBook={!isRecruiter ? () => openBooking(contact) : null}
                  />
                ))}
              </div>
            )}

            <section className="booking-section">
              <div className="section-heading">
                <div>
                  <p className="eyebrow">{isRecruiter ? 'Requests' : 'Requests'}</p>
                  <h2>{isRecruiter ? 'Incoming booking requests' : 'My bookings'}</h2>
                </div>
                <span className="count-pill">{myBookings.length} booking{myBookings.length === 1 ? '' : 's'}</span>
              </div>
              {bookingsLoading ? (
                <div className="dashboard-state">Loading bookings...</div>
              ) : myBookings.length === 0 ? (
                <div className="empty-state"><h3>No bookings yet</h3><p>{isRecruiter ? 'Booking requests from customers will appear here.' : 'Book a recruiter to create your first request.'}</p></div>
              ) : (
                <div className="booking-grid">
                  {myBookings.map((booking) => (
                    <BookingCard
                      key={booking.id}
                      booking={booking}
                      isRecruiter={isRecruiter}
                      onStatus={handleBookingStatus}
                      onComplete={handleCompleteBooking}
                      actionLoading={actionLoading}
                    />
                  ))}
                </div>
              )}
            </section>
          </>
        )}
      </main>

      {selectedRecruiter && (
        <BookingModal
          recruiter={selectedRecruiter}
          form={form}
          setForm={setForm}
          onClose={closeBookingModal}
          onSubmit={handleCreateBooking}
          submitting={submitting}
        />
      )}
    </div>
  )
}

function contactLabel(isRecruiter) {
  return isRecruiter ? 'Customer' : 'Recruiter'
}
