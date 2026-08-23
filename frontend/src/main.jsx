import React, { useEffect, useMemo, useState } from 'react'
import { createRoot } from 'react-dom/client'
import { CarFront, CircleUserRound, Gauge, LogOut, Plus, Search, ShieldCheck, SlidersHorizontal, X, User, MapPin, Phone, Save, Trash2 } from 'lucide-react'
import './styles.css'

// In development the API runs on port 8000.  On Vercel, the FastAPI app is
// served by this same site under /api, so an empty base keeps requests
// same-origin and avoids CORS/localhost failures for visitors.
const API = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? 'http://localhost:8000' : '')
const demoVehicles = [
  { id: 1, make: 'Porsche', model: '911 Carrera', category: 'Sports', price: 126000, quantity: 2 },
  { id: 2, make: 'Range Rover', model: 'Velar Dynamic', category: 'SUV', price: 68900, quantity: 4 },
  { id: 3, make: 'Mercedes-Benz', model: 'S 580 4MATIC', category: 'Luxury', price: 128400, quantity: 1 },
  { id: 4, make: 'Tesla', model: 'Model S Plaid', category: 'Electric', price: 89990, quantity: 0 },
]
const money = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 })

function api(path, method = 'GET', body, token) {
  return fetch(`${API}${path}`, { method, headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) }, ...(body ? { body: JSON.stringify(body) } : {}) }).then(async r => {
    if (r.status === 401) {
      // Clear invalid session
      localStorage.removeItem('apex-session')
      window.location.reload()
      throw new Error('Session expired. Please log in again.')
    }
    const data = r.status === 204 ? null : await r.json()
    if (!r.ok) throw new Error(data?.detail || 'Something went wrong')
    return data
  })
}

function AuthPanel({ onSuccess }) {
  const [mode, setMode] = useState('login'), [form, setForm] = useState({ name: '', email: '', password: '' }), [error, setError] = useState(''), [loading, setLoading] = useState(false)
  const isLogin = mode === 'login' || mode === 'admin'
  const submit = async e => {
    e.preventDefault(); setLoading(true); setError('')
    try {
      const result = await api(isLogin ? '/api/auth/login' : '/api/auth/register', 'POST', isLogin ? { email: form.email, password: form.password } : form)
      if (isLogin) {
        if (mode === 'admin' && result.user.role !== 'admin') throw new Error('This account does not have administrator access.')
        onSuccess(result)
      } else { setMode('login'); setError('Account created. Please sign in.') }
    } catch (err) { setError(err.message) } finally { setLoading(false) }
  }
  const changeMode = next => { setMode(next); setError('') }
  return <main className="auth-shell"><section className="auth-story"><div className="brand"><CarFront size={27} /><span>APEX<span className="text-gold">MOTORS</span></span></div><p className="eyebrow">EXCEPTIONAL, BY DESIGN</p><h1>Inventory,<br /><em>elevated.</em></h1><p className="story-copy">A considered workspace for the modern dealership—where every detail moves with intent.</p><div className="story-stat"><b>240+</b><span>vehicles curated<br />across four collections</span></div></section><section className="auth-card"><div><p className="eyebrow text-gold">{mode === 'admin' ? 'ADMINISTRATOR ACCESS' : 'WELCOME TO APEX'}</p><h2>{mode === 'register' ? 'Create your account' : mode === 'admin' ? 'Admin sign in' : 'Sign in to your account'}</h2><p className="muted">{mode === 'admin' ? 'Manage inventory, stock, and customer accounts.' : mode === 'register' ? 'Start exploring the collection.' : 'Access the showroom inventory.'}</p></div><form onSubmit={submit}>{mode === 'register' && <label>Full name<input required minLength="2" placeholder="Your name" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} /></label>}<label>Email address<input required type="email" placeholder="name@example.com" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} /></label><label>Password<input required minLength="8" type="password" placeholder="••••••••" value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} /></label>{error && <p className="form-message">{error}</p>}<button className="primary" disabled={loading}>{loading ? 'Please wait…' : mode === 'register' ? 'Create account' : 'Sign in'} <span>→</span></button></form><p className="switcher">{mode === 'register' ? 'Already registered?' : mode === 'admin' ? 'Not an administrator?' : 'New to Apex?'} <button onClick={() => changeMode(mode === 'register' ? 'login' : mode === 'admin' ? 'login' : 'register')}>{mode === 'register' ? 'Sign in' : mode === 'admin' ? 'Customer sign in' : 'Create an account'}</button></p>{mode !== 'admin' && <p className="switcher"><button onClick={() => changeMode('admin')}>Administrator sign in</button></p>}</section></main>
}

export function VehicleCard({ vehicle, onPurchase, admin, onEdit }) { const out = vehicle.quantity === 0; return <article className="vehicle-card"><div className={`car-art art-${vehicle.id % 4}`}><CarFront strokeWidth={1.1} size={88} /><span>{vehicle.category}</span></div><div className="vehicle-info"><div><p className="vehicle-make">{vehicle.make}</p><h3>{vehicle.model}</h3></div><p className="price">{money.format(vehicle.price)}</p></div><div className="vehicle-footer"><span className={out ? 'stock out' : 'stock'}>{out ? 'Out of stock' : `${vehicle.quantity} in stock`}</span>{admin ? <button className="secondary" onClick={() => onEdit(vehicle)}>Manage</button> : <button disabled={out} className="secondary" onClick={() => onPurchase(vehicle)}>{out ? 'Unavailable' : 'Purchase'}</button>}</div></article> }

function VehicleForm({ vehicle, onClose, onSave, onDelete, onRestock }) { const [form, setForm] = useState(vehicle || { make: '', model: '', category: 'SUV', price: '', quantity: 1 }); const [restockQty, setRestockQty] = useState(1); const submit = e => { e.preventDefault(); onSave({ ...form, price: Number(form.price), quantity: Number(form.quantity) }) }; return <div className="modal-backdrop"><form className="modal" onSubmit={submit}><button type="button" className="close" onClick={onClose}><X /></button><p className="eyebrow text-gold">ADMIN INVENTORY</p><h2>{vehicle ? 'Update vehicle' : 'Add a vehicle'}</h2><div className="grid-fields"><label>Make<input required value={form.make} onChange={e => setForm({ ...form, make: e.target.value })} /></label><label>Model<input required value={form.model} onChange={e => setForm({ ...form, model: e.target.value })} /></label><label>Category<select value={form.category} onChange={e => setForm({ ...form, category: e.target.value })}>{['SUV', 'Sports', 'Luxury', 'Electric', 'Sedan'].map(x => <option key={x}>{x}</option>)}</select></label><label>Price<input required min="1" type="number" value={form.price} onChange={e => setForm({ ...form, price: e.target.value })} /></label><label>Stock quantity<input required min="0" type="number" value={form.quantity} onChange={e => setForm({ ...form, quantity: e.target.value })} /></label></div>{vehicle && <div className="restock-row"><label>Quick restock<input min="1" type="number" value={restockQty} onChange={e => setRestockQty(e.target.value)} /></label><button type="button" className="secondary" onClick={() => onRestock(vehicle, Number(restockQty))}>Add stock</button></div>}<div className="modal-actions"><button className="primary">Save vehicle <span>→</span></button>{vehicle && <button type="button" className="danger" onClick={() => onDelete(vehicle)}>Delete</button>}</div></form></div> }

function ProfileForm({ user, onClose, onUpdate }) {
  const [form, setForm] = useState({
    name: user.name || '',
    phone: user.phone || '',
    address: user.address || '',
    city: user.city || '',
    state: user.state || '',
    zip_code: user.zip_code || '',
    country: user.country || ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const submit = async e => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      await onUpdate(form)
      onClose()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="modal-backdrop">
      <form className="modal" onSubmit={submit}>
        <button type="button" className="close" onClick={onClose}><X /></button>
        <p className="eyebrow text-gold">PROFILE SETTINGS</p>
        <h2>Edit your profile</h2>
        
        <div className="grid-fields">
          <label>Full name<input required value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} /></label>
          <label>Phone<input value={form.phone} onChange={e => setForm({ ...form, phone: e.target.value })} /></label>
          <label>Address<input value={form.address} onChange={e => setForm({ ...form, address: e.target.value })} /></label>
          <label>City<input value={form.city} onChange={e => setForm({ ...form, city: e.target.value })} /></label>
          <label>State<input value={form.state} onChange={e => setForm({ ...form, state: e.target.value })} /></label>
          <label>ZIP Code<input value={form.zip_code} onChange={e => setForm({ ...form, zip_code: e.target.value })} /></label>
          <label>Country<input value={form.country} onChange={e => setForm({ ...form, country: e.target.value })} /></label>
        </div>

        {error && <p className="form-message">{error}</p>}
        
        <div className="modal-actions">
          <button className="primary" disabled={loading}>
            {loading ? 'Saving…' : 'Save changes'} <Save size={16} />
          </button>
        </div>
      </form>
    </div>
  )
}

function UserManagement({ token, currentUser, onNotice }) {
  const [users, setUsers] = useState([]), [loading, setLoading] = useState(true)
  const loadUsers = async () => { setLoading(true); try { setUsers(await api('/api/admin/users', 'GET', null, token)) } catch (error) { onNotice(error.message) } finally { setLoading(false) } }
  useEffect(() => { loadUsers() }, [token])
  const update = async (user, changes) => { try { const updated = await api(`/api/admin/users/${user.id}`, 'PUT', changes, token); setUsers(items => items.map(item => item.id === updated.id ? updated : item)); onNotice(`${updated.name}'s account was updated.`) } catch (error) { onNotice(error.message) } }
  const remove = async user => { if (!window.confirm(`Remove ${user.name}'s account? This cannot be undone.`)) return; try { await api(`/api/admin/users/${user.id}`, 'DELETE', null, token); setUsers(items => items.filter(item => item.id !== user.id)); onNotice('User account removed.') } catch (error) { onNotice(error.message) } }
  if (loading) return <p className="empty-state">Loading customer accounts…</p>
  return <section className="user-list">{users.map(user => <article className="user-row" key={user.id}><div><b>{user.name}</b><span>{user.email} · Joined {new Date(user.created_at).toLocaleDateString()}</span></div><div className="user-controls"><select aria-label={`Role for ${user.name}`} value={user.role} disabled={user.id === currentUser.id} onChange={e => update(user, { role: e.target.value })}><option value="user">Customer</option><option value="admin">Administrator</option></select><label className="verify"><input type="checkbox" checked={user.email_verified} onChange={e => update(user, { email_verified: e.target.checked })} /> Verified</label>{user.id !== currentUser.id && <button className="danger-icon" aria-label={`Delete ${user.name}`} onClick={() => remove(user)}><Trash2 size={16} /></button>}</div></article>)}</section>
}

function AdminOrderManagement({ token, vehicles, onNotice }) {
  const [orders, setOrders] = useState([]), [customers, setCustomers] = useState([]), [loading, setLoading] = useState(true)
  useEffect(() => {
    Promise.all([api('/api/admin/orders', 'GET', null, token), api('/api/admin/users', 'GET', null, token)])
      .then(([allOrders, allUsers]) => { setOrders(allOrders); setCustomers(allUsers) })
      .catch(error => onNotice(error.message)).finally(() => setLoading(false))
  }, [token])
  const updateStatus = async (order, status) => {
    try { const updated = await api(`/api/orders/${order.id}`, 'PUT', { status }, token); setOrders(items => items.map(item => item.id === updated.id ? updated : item)); onNotice(`Order #${order.id} marked ${status}.`) }
    catch (error) { onNotice(error.message) }
  }
  if (loading) return <p className="empty-state">Loading dealership orders…</p>
  if (!orders.length) return <p className="empty-state">No customer purchases yet.</p>
  return <section className="user-list">{orders.map(order => { const customer = customers.find(user => user.id === order.user_id); const vehicle = vehicles.find(item => item.id === order.vehicle_id); return <article className="user-row" key={order.id}><div><b>{vehicle ? `${vehicle.make} ${vehicle.model}` : `Vehicle #${order.vehicle_id}`}</b><span>Order #{order.id} · {customer?.name || 'Customer'} ({customer?.email || 'account removed'}) · {money.format(order.total_amount)}</span></div><div className="user-controls"><span className="order-date">{new Date(order.purchased_at).toLocaleDateString()}</span><select aria-label={`Status for order ${order.id}`} value={order.status} onChange={e => updateStatus(order, e.target.value)}>{['pending', 'confirmed', 'processing', 'completed', 'cancelled'].map(status => <option key={status}>{status}</option>)}</select></div></article> })}</section>
}

function Dashboard({ session, onLogout, onSessionUpdate }) {
  const [vehicles, setVehicles] = useState([]), [search, setSearch] = useState(''), [category, setCategory] = useState('All'), [notice, setNotice] = useState(''), [modal, setModal] = useState(null), [activeTab, setActiveTab] = useState('inventory'), [orders, setOrders] = useState([]), [userProfile, setUserProfile] = useState(session.user)
  const admin = session.user.role === 'admin'
  useEffect(() => { api('/api/vehicles', 'GET', null, session.access_token).then(r => setVehicles(r.items)).catch(() => setVehicles(demoVehicles)) }, [session.access_token])
  const loadCustomerOrders = async () => {
    try { setOrders(await api('/api/orders', 'GET', null, session.access_token)) }
    catch (error) { setNotice(error.message) }
  }
  useEffect(() => { if (!admin) loadCustomerOrders() }, [session.access_token, admin])
  const filtered = useMemo(() => vehicles.filter(v => `${v.make} ${v.model}`.toLowerCase().includes(search.toLowerCase()) && (category === 'All' || v.category === category)), [vehicles, search, category])
  const purchase = async v => { 
    try { 
      const updated = await api(`/api/vehicles/${v.id}/purchase`, 'POST', { vehicle_id: v.id, quantity: 1 }, session.access_token); 
      setVehicles(xs => xs.map(x => x.id === v.id ? updated : x)); 
      setNotice(`${v.make} ${v.model} reserved successfully.`)
      await loadCustomerOrders()
    } catch (e) { 
      setNotice(e.message) 
    } 
  }
  const restock = async (vehicle, quantity) => { try { const updated = await api(`/api/vehicles/${vehicle.id}/restock`, 'POST', { quantity }, session.access_token); setVehicles(xs => xs.map(x => x.id === updated.id ? updated : x)); setModal(updated); setNotice(`${quantity} units added to inventory.`) } catch (e) { setNotice(e.message) } }
  const remove = async vehicle => { if (!window.confirm(`Delete ${vehicle.make} ${vehicle.model}? This cannot be undone.`)) return; try { await api(`/api/vehicles/${vehicle.id}`, 'DELETE', null, session.access_token); setVehicles(xs => xs.filter(x => x.id !== vehicle.id)); setModal(null); setNotice('Vehicle removed from inventory.') } catch (e) { setNotice(e.message) } }
  const save = async data => { try { const updated = await api(modal?.id ? `/api/vehicles/${modal.id}` : '/api/vehicles', modal?.id ? 'PUT' : 'POST', data, session.access_token); setVehicles(xs => modal?.id ? xs.map(x => x.id === updated.id ? updated : x) : [updated, ...xs]); setModal(null); setNotice('Inventory updated.') } catch (e) { setNotice(e.message) } }
  const updateProfile = async data => { try { const updated = await api('/api/user/profile', 'PUT', data, session.access_token); setUserProfile(updated); const updatedSession = { ...session, user: updated }; localStorage.setItem('apex-session', JSON.stringify(updatedSession)); if (onSessionUpdate) onSessionUpdate(updatedSession); setNotice('Profile updated successfully.') } catch (e) { setNotice(e.message) } }
  
  const renderContent = () => {
    if (activeTab === 'inventory') {
      return (
        <>
          <section className="hero">
            <div>
              <p className="eyebrow text-gold">THE COLLECTION</p>
              <h1>Find your next<br /><em>exceptional</em> drive.</h1>
              <p>Explore our precisely curated inventory of performance, luxury, and electric vehicles.</p>
            </div>
            <div className="hero-metric">
              <Gauge size={22} />
              <b>{vehicles.length || '—'}</b>
              <span>vehicles<br />in inventory</span>
            </div>
          </section>
          <section className="toolbar">
            <div className="search">
              <Search size={19} />
              <input placeholder="Search make or model" value={search} onChange={e => setSearch(e.target.value)} />
            </div>
            <div className="filters">
              <SlidersHorizontal size={18} />
              {['All', 'SUV', 'Sports', 'Luxury', 'Electric'].map(x => (
                <button className={category === x ? 'selected' : ''} key={x} onClick={() => setCategory(x)}>{x}</button>
              ))}
            </div>
            {admin && <button className="add-button" onClick={() => setModal({})}><Plus size={18} /> Add vehicle</button>}
          </section>
          {notice && <div className="notice">{notice}<button onClick={() => setNotice('')}>×</button></div>}
          <div className="results">
            <p><b>{filtered.length}</b> vehicles available</p>
            <span>Showing curated inventory</span>
          </div>
          <section className="inventory-grid">
            {filtered.map(v => <VehicleCard key={v.id} vehicle={v} onPurchase={purchase} admin={admin} onEdit={setModal} />)}
          </section>
        </>
      )
    } else if (activeTab === 'insights') {
      const totalValue = vehicles.reduce((sum, v) => sum + (v.price * v.quantity), 0)
      const categoryStats = vehicles.reduce((acc, v) => {
        acc[v.category] = (acc[v.category] || 0) + 1
        return acc
      }, {})
      const lowStock = vehicles.filter(v => v.quantity < 3).length
      const outOfStock = vehicles.filter(v => v.quantity === 0).length

      return (
        <>
          <section className="hero">
            <div>
              <p className="eyebrow text-gold">INSIGHTS</p>
              <h1>Performance<br /><em>analytics</em></h1>
              <p>Track your dealership performance with real-time metrics and trends.</p>
            </div>
            <div className="hero-metric">
              <Gauge size={22} />
              <b>{vehicles.length}</b>
              <span>total<br />vehicles</span>
            </div>
          </section>
          <section className="toolbar">
            {notice && <div className="notice">{notice}<button onClick={() => setNotice('')}>×</button></div>}
          </section>
          <div className="results">
            <p><b>Key Metrics</b></p>
            <span>Real-time inventory analytics</span>
          </div>
          <section className="inventory-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))' }}>
            <article className="vehicle-card">
              <div className="vehicle-info">
                <div>
                  <p className="vehicle-make">Total Inventory Value</p>
                  <h3>{money.format(totalValue)}</h3>
                </div>
                <p className="price" style={{ fontSize: '0.85rem', color: '#d4a854' }}>Assets</p>
              </div>
              <div className="vehicle-footer">
                <span className="stock">{vehicles.length} vehicles</span>
              </div>
            </article>
            <article className="vehicle-card">
              <div className="vehicle-info">
                <div>
                  <p className="vehicle-make">Low Stock Alert</p>
                  <h3>{lowStock} vehicles</h3>
                </div>
                <p className="price" style={{ fontSize: '0.85rem', color: '#ff6b6b' }}>Action needed</p>
              </div>
              <div className="vehicle-footer">
                <span className="stock out">Below 3 units</span>
              </div>
            </article>
            <article className="vehicle-card">
              <div className="vehicle-info">
                <div>
                  <p className="vehicle-make">Out of Stock</p>
                  <h3>{outOfStock} vehicles</h3>
                </div>
                <p className="price" style={{ fontSize: '0.85rem', color: '#ff6b6b' }}>Critical</p>
              </div>
              <div className="vehicle-footer">
                <span className="stock out">Unavailable</span>
              </div>
            </article>
            <article className="vehicle-card">
              <div className="vehicle-info">
                <div>
                  <p className="vehicle-make">Total Orders</p>
                  <h3>{orders.length}</h3>
                </div>
                <p className="price" style={{ fontSize: '0.85rem', color: '#d4a854' }}>Sales</p>
              </div>
              <div className="vehicle-footer">
                <span className="stock">All time</span>
              </div>
            </article>
          </section>
          <div className="results" style={{ marginTop: '2rem' }}>
            <p><b>Category Distribution</b></p>
            <span>Inventory by vehicle type</span>
          </div>
          <section className="inventory-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))' }}>
            {Object.entries(categoryStats).map(([category, count]) => (
              <article key={category} className="vehicle-card">
                <div className="vehicle-info">
                  <div>
                    <p className="vehicle-make">{category}</p>
                    <h3>{count} vehicles</h3>
                  </div>
                  <p className="price">{Math.round((count / vehicles.length) * 100)}%</p>
                </div>
                <div className="vehicle-footer">
                  <span className="stock">{count} in stock</span>
                </div>
              </article>
            ))}
          </section>
        </>
      )
    } else if (activeTab === 'orders' && admin) {
      return <><section className="hero"><div><p className="eyebrow text-gold">ADMINISTRATION</p><h1>Sales<br /><em>queue</em></h1><p>Review every customer purchase and keep order fulfilment moving.</p></div><div className="hero-metric"><Gauge size={22} /><b>All</b><span>customer<br />orders</span></div></section>{notice && <div className="notice">{notice}<button onClick={() => setNotice('')}>×</button></div>}<div className="results"><p><b>Dealership orders</b></p><span>Update fulfilment status</span></div><AdminOrderManagement token={session.access_token} vehicles={vehicles} onNotice={setNotice} /></>
    } else if (activeTab === 'orders') {
      return (
        <>
          <section className="hero">
            <div>
              <p className="eyebrow text-gold">ORDERS</p>
              <h1>Order<br /><em>history</em></h1>
              <p>View your recent vehicle reservations and purchases.</p>
            </div>
            <div className="hero-metric">
              <Gauge size={22} />
              <b>{orders.length}</b>
              <span>total<br />orders</span>
            </div>
          </section>
          <section className="toolbar">
            {notice && <div className="notice">{notice}<button onClick={() => setNotice('')}>×</button></div>}
          </section>
          <div className="results">
            <p><b>{orders.length}</b> orders</p>
            <span>Showing order history</span>
          </div>
          <section className="inventory-grid">
            {orders.length === 0 ? (
              <p style={{ gridColumn: '1/-1', textAlign: 'center', padding: '2rem', color: '#888' }}>No orders yet. Start by purchasing a vehicle from the inventory.</p>
            ) : (
              orders.map(order => {
                const vehicle = vehicles.find(item => item.id === order.vehicle_id)
                return <article key={order.id} className="vehicle-card">
                  <div className="vehicle-info">
                    <div>
                      <p className="vehicle-make">{vehicle?.make || 'Vehicle'}</p>
                      <h3>{vehicle?.model || `Vehicle #${order.vehicle_id}`}</h3>
                    </div>
                    <p className="price">{money.format(order.total_amount)}</p>
                  </div>
                  <div className="vehicle-footer">
                    <span className="stock">{order.status}</span>
                    <span style={{ fontSize: '0.85rem', color: '#888' }}>{new Date(order.purchased_at).toLocaleDateString()}</span>
                  </div>
                </article>
              })
            )}
          </section>
        </>
      )
    } else if (activeTab === 'users' && admin) {
      return <><section className="hero"><div><p className="eyebrow text-gold">ADMINISTRATION</p><h1>Customer<br /><em>accounts</em></h1><p>Manage access levels and verify customer accounts.</p></div><div className="hero-metric"><User size={22} /><b>Users</b><span>account<br />management</span></div></section>{notice && <div className="notice">{notice}<button onClick={() => setNotice('')}>×</button></div>}<div className="results"><p><b>All accounts</b></p><span>Role and verification controls</span></div><UserManagement token={session.access_token} currentUser={session.user} onNotice={setNotice} /></>
    } else if (activeTab === 'profile') {
      return (
        <>
          <section className="hero">
            <div>
              <p className="eyebrow text-gold">PROFILE</p>
              <h1>Account<br /><em>settings</em></h1>
              <p>Manage your personal information and preferences.</p>
            </div>
            <div className="hero-metric">
              <User size={22} />
              <b>{userProfile.name || 'User'}</b>
              <span>account<br />holder</span>
            </div>
          </section>
          <section className="toolbar">
            {notice && <div className="notice">{notice}<button onClick={() => setNotice('')}>×</button></div>}
          </section>
          <div className="results">
            <p><b>Personal Information</b></p>
            <span>Update your contact details</span>
          </div>
          <section className="inventory-grid" style={{ gridTemplateColumns: '1fr' }}>
            <article className="vehicle-card" style={{ padding: '2rem' }}>
              <div className="vehicle-info">
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
                  <CircleUserRound size={48} style={{ color: '#d4a854' }} />
                  <div>
                    <h3 style={{ margin: 0 }}>{userProfile.name || 'Not set'}</h3>
                    <p className="vehicle-make" style={{ margin: 0, fontSize: '0.9rem' }}>{userProfile.email}</p>
                  </div>
                </div>
                <div style={{ display: 'grid', gap: '0.5rem', marginTop: '1rem' }}>
                  {userProfile.phone && <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}><Phone size={16} /> {userProfile.phone}</div>}
                  {userProfile.address && <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}><MapPin size={16} /> {userProfile.address}, {userProfile.city}, {userProfile.state} {userProfile.zip_code}</div>}
                  {userProfile.country && <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}><MapPin size={16} /> {userProfile.country}</div>}
                </div>
              </div>
              <div className="vehicle-footer">
                <span className="stock">{userProfile.email_verified ? 'Verified' : 'Unverified'}</span>
                <button className="secondary" onClick={() => setModal('profile')}>Edit Profile</button>
              </div>
            </article>
          </section>
        </>
      )
    }
  }
  
  return (
    <div className="app-shell">
      <header>
        <div className="brand"><CarFront size={24} /><span>APEX<span className="text-gold">MOTORS</span></span></div>
        <nav>
          <a className={activeTab === 'inventory' ? 'active' : ''} onClick={() => setActiveTab('inventory')}>Inventory</a>
          <a className={activeTab === 'insights' ? 'active' : ''} onClick={() => setActiveTab('insights')}>Insights</a>
          <a className={activeTab === 'orders' ? 'active' : ''} onClick={() => setActiveTab('orders')}>{admin ? 'Sales' : 'Orders'}</a>
          {admin && <a className={activeTab === 'users' ? 'active' : ''} onClick={() => setActiveTab('users')}>Users</a>}
          <a className={activeTab === 'profile' ? 'active' : ''} onClick={() => setActiveTab('profile')}>Profile</a>
        </nav>
        <div className="profile">
          <span className="role"><ShieldCheck size={15} /> {admin ? 'Administrator' : 'Client access'}</span>
          <CircleUserRound size={23} />
          <button aria-label="Sign out" onClick={onLogout}><LogOut size={18} /></button>
        </div>
      </header>
      <main className="dashboard">
        {renderContent()}
      </main>
      {modal === 'profile' ? (
        <ProfileForm user={userProfile} onClose={() => setModal(null)} onUpdate={updateProfile} />
      ) : modal && (
        <VehicleForm vehicle={modal.id ? modal : null} onClose={() => setModal(null)} onSave={save} onDelete={remove} onRestock={restock} />
      )}
    </div>
  )
}

export function App() { const [session, setSession] = useState(() => { try { return JSON.parse(localStorage.getItem('apex-session')) } catch { return null } }); const enter = data => { localStorage.setItem('apex-session', JSON.stringify(data)); setSession(data) }; const leave = () => { localStorage.removeItem('apex-session'); setSession(null) }; const updateSession = (updatedSession) => { setSession(updatedSession) }; return session ? <Dashboard session={session} onLogout={leave} onSessionUpdate={updateSession} /> : <AuthPanel onSuccess={enter} /> }
const root = document.getElementById('root')
if (root) createRoot(root).render(<App />)
