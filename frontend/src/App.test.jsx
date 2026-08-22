import { fireEvent, render, screen } from '@testing-library/react'
import { VehicleCard } from './main.jsx'

const vehicle = { id: 1, make: 'Tesla', model: 'Model S Plaid', category: 'Electric', price: 89990, quantity: 0 }

test('disables purchase for an out-of-stock vehicle', () => {
  render(<VehicleCard vehicle={vehicle} admin={false} onPurchase={() => {}} />)
  expect(screen.getByRole('button', { name: 'Unavailable' }).disabled).toBe(true)
})

test('offers admin management action to administrators', () => {
  const edit = vi.fn()
  render(<VehicleCard vehicle={{ ...vehicle, quantity: 2 }} admin onEdit={edit} />)
  fireEvent.click(screen.getByRole('button', { name: 'Manage' }))
  expect(edit).toHaveBeenCalledWith(expect.objectContaining({ id: 1 }))
})
