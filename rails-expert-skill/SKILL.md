---
name: rails-expert
description: Rails 7+ specialist with expertise in Hotwire, Turbo, Stimulus, and modern Rails development
---

# Rails Expert

## Core Capabilities

### Rails 7+ Modern Features
- **Hotwire**: Turbo, Stimulus, and dynamic HTML updates without JavaScript frameworks
- **Import Maps**: JavaScript dependency management without build tools
- **Rails 7 Action Text**: Rich text editing with modern UI
- **Encrypted Credentials**: Enhanced security for sensitive data
- **Async Query Loading**: Improved database query performance
- **Multi-DB Support**: Primary/replica database configurations
- **Parallel Testing**: Faster test execution across processes
- **Async Action Mailer**: Non-blocking email delivery

### Hotwire Stack
- **Turbo Drive**: Faster page navigation with automatic page caching
- **Turbo Frames**: Partial page updates without full reloads
- **Turbo Streams**: Real-time updates over WebSocket or SSE
- **Stimulus Controllers**: Structured client-side JavaScript behavior
- **Turbo Morph**: Smart DOM diffing for minimal re-renders

### Modern Rails Patterns
- **Service Objects**: Extract business logic from controllers
- **Query Objects**: Complex database queries as reusable objects
- **Form Objects**: Handle complex form logic and validation
- **Decorators**: Presentational logic separation
- **View Components**: Reusable UI component architecture
- **API Resources**: Consistent API response formatting

## Architecture Patterns

### Modern Rails Application Structure
```ruby
# app/models/order.rb
class Order < ApplicationRecord
  belongs_to :customer
  has_many :order_items, dependent: :destroy
  has_many :products, through: :order_items

  # Modern enum with i18n support
  enum :status, { pending: 'pending', processing: 'processing', completed: 'completed', cancelled: 'cancelled' },
       suffix: true

  # Rich validations with custom error messages
  validates :customer, presence: { message: 'Customer is required' }
  validates :order_items, presence: true, length: { minimum: 1, message: 'Order must contain at least one item' }
  validates :total_amount, numericality: { greater_than: 0 }, allow_nil: true

  # Scopes with proper chaining
  scope :recent, -> { order(created_at: :desc) }
  scope :by_customer, ->(customer_id) { where(customer_id:) }
  scope :with_status, ->(status) { where(status:) }
  scope :in_date_range, ->(start_date, end_date) { where(created_at: start_date..end_date) }

  # Delegates for cleaner interfaces
  delegate :name, :email, to: :customer, prefix: true

  # Callbacks with proper error handling
  before_save :calculate_total_amount
  after_create :send_confirmation_email
  after_update :log_status_change, if: :saved_change_to_status?

  # Money handling with Rails 7 attributes
  attribute :total_amount_cents, :integer, default: 0

  # Virtual attribute for money formatting
  def total_amount
    Money.new(total_amount_cents || 0)
  end

  def total_amount=(value)
    self.total_amount_cents = Money.from_amount(value).cents
  end

  # Business logic methods
  def can_transition_to?(new_status)
    status_transitions = {
      'pending' => ['processing', 'cancelled'],
      'processing' => ['completed', 'cancelled'],
      'completed' => [],
      'cancelled' => []
    }
    status_transitions[status]&.include?(new_status.to_s)
  end

  def transition_to!(new_status)
    unless can_transition_to?(new_status)
      raise ArgumentError, "Cannot transition from #{status} to #{new_status}"
    end

    update!(status: new_status)
  end

  # Calculations with caching
  def item_count
    Rails.cache.fetch("order_#{id}_item_count", expires_in: 1.hour) do
      order_items.sum(:quantity)
    end
  end

  private

  def calculate_total_amount
    self.total_amount_cents = order_items.sum { |item| item.quantity * item.unit_price_cents }
  end

  def send_confirmation_email
    OrderMailer.confirmation(self).deliver_later
  end

  def log_status_change
    Rails.logger.info "Order #{id} status changed from #{saved_change_to_status[0]} to #{status}"
  end
end

# app/models/order_item.rb
class OrderItem < ApplicationRecord
  belongs_to :order
  belongs_to :product

  validates :quantity, numericality: { greater_than: 0 }
  validates :unit_price_cents, numericality: { greater_than: 0 }

  delegate :name, to: :product, prefix: true

  attribute :unit_price_cents, :integer

  def unit_price
    Money.new(unit_price_cents)
  end

  def unit_price=(value)
    self.unit_price_cents = Money.from_amount(value).cents
  end

  def total_price
    Money.new(quantity * unit_price_cents)
  end
end
```

### Service Objects Pattern
```ruby
# app/services/order_service.rb
class OrderService
  include ActiveModel::Model
  include ActiveModel::Attributes
  include ActiveModel::Validations

  attribute :customer_id, :integer
  attribute :items, array: true

  validates :customer_id, presence: true
  validates :items, presence: true, length: { minimum: 1 }

  attr_reader :order

  def initialize(attributes = {})
    super
    @items = build_items_attributes(attributes[:items] || [])
  end

  def create
    return false unless valid?

    ActiveRecord::Base.transaction do
      @order = Order.create!(customer_id:)
      create_order_items
      calculate_and_save_total
      process_payment
      send_notifications
    end

    true
  rescue ActiveRecord::RecordInvalid, ActiveRecord::RecordNotSaved => e
    errors.add(:base, e.message)
    false
  rescue StandardError => e
    errors.add(:base, 'Order creation failed. Please try again.')
    Rails.logger.error "Order creation failed: #{e.message}"
    false
  end

  private

  def build_items_attributes(items_data)
    items_data.map do |item_data|
      {
        product_id: item_data[:product_id],
        quantity: item_data[:quantity],
        unit_price: item_data[:unit_price]
      }
    end
  end

  def create_order_items
    items.each do |item_data|
      product = Product.find(item_data[:product_id])
      
      unless product.available?(item_data[:quantity])
        raise ArgumentError, "Insufficient stock for product #{product.name}"
      end

      order.order_items.create!(
        product: product,
        quantity: item_data[:quantity],
        unit_price: product.price
      )
    end
  end

  def calculate_and_save_total
    total = order.order_items.sum { |item| item.quantity * item.unit_price_cents }
    order.update!(total_amount_cents: total)
  end

  def process_payment
    PaymentProcessor.new(order).process_payment
  end

  def send_notifications
    OrderMailer.confirmation(order).deliver_later
    ProductStockService.new(order.order_items).reserve_stock
  end
end

# app/services/payment_processor.rb
class PaymentProcessor
  include ActiveModel::Model

  attr_reader :order

  def initialize(order)
    @order = order
  end

  def process_payment
    payment_intent = create_stripe_payment_intent
    order.update!(stripe_payment_intent_id: payment_intent.id)
    
    payment_intent
  rescue Stripe::StripeError => e
    raise PaymentError, "Payment processing failed: #{e.message}"
  end

  def confirm_payment(payment_intent_id)
    payment_intent = Stripe::PaymentIntent.retrieve(payment_intent_id)
    
    if payment_intent.status == 'succeeded'
      order.update!(payment_status: :paid, paid_at: Time.current)
      order.transition_to!(:processing)
    else
      order.update!(payment_status: :failed)
    end
    
    payment_intent
  end

  private

  def create_stripe_payment_intent
    Stripe::PaymentIntent.create(
      amount: order.total_amount_cents,
      currency: 'usd',
      metadata: {
        order_id: order.id,
        customer_id: order.customer_id
      },
      receipt_email: order.customer_email
    )
  end
end
```

### Modern Controllers with Hotwire
```ruby
# app/controllers/orders_controller.rb
class OrdersController < ApplicationController
  before_action :authenticate_user!
  before_action :set_order, only: [:show, :update, :destroy]

  # Index with Turbo Frames for pagination
  def index
    @orders = policy_scope(Order)
                 .includes(:customer, :order_items)
                 .by_customer(params[:customer_id])
                 .with_status(params[:status])
                 .in_date_range(date_range_params)
                 .page(params[:page])
                 .per(20)

    respond_to do |format|
      format.html
      format.turbo_stream { render partial: 'orders', locals: { orders: @orders } }
    end
  end

  def show
    @order_items = @order.order_items.includes(:product)
  end

  def new
    @order_service = OrderService.new
    @products = Product.available.order(:name)
  end

  def create
    @order_service = OrderService.new(order_params)

    if @order_service.create
      redirect_to @order_service.order, notice: 'Order was successfully created.'
    else
      @products = Product.available.order(:name)
      render :new, status: :unprocessable_entity
    end
  end

  def update
    if @order.update(order_update_params)
      respond_to do |format|
        format.html { redirect_to @order, notice: 'Order was successfully updated.' }
        format.turbo_stream { render turbo_stream: turbo_stream.replace(@order, partial: 'orders/order', locals: { order: @order }) }
      end
    else
      respond_to do |format|
        format.html { render :show, status: :unprocessable_entity }
        format.turbo_stream { render turbo_stream: turbo_stream.replace("order_#{@order.id}", partial: 'orders/order_form', locals: { order: @order }) }
      end
    end
  end

  def destroy
    @order.transition_to!(:cancelled)
    redirect_to orders_url, notice: 'Order was successfully cancelled.'
  end

  # Turbo Stream action for real-time status updates
  def update_status
    new_status = params[:status].to_sym
    
    if @order.can_transition_to?(new_status)
      @order.transition_to!(new_status)
      broadcast_order_update
      render turbo_stream: turbo_stream.replace(
        "order_#{@order.id}",
        partial: 'orders/order_row',
        locals: { order: @order }
      )
    else
      render turbo_stream: turbo_stream.replace(
        "order_#{@order.id}_errors",
        partial: 'shared/alert',
        locals: { alert_type: 'error', message: 'Invalid status transition' }
      )
    end
  end

  private

  def set_order
    @order = Order.find(params[:id])
    authorize @order
  end

  def order_params
    params.require(:order_service).permit(:customer_id, items: [:product_id, :quantity, :unit_price])
  end

  def order_update_params
    params.require(:order).permit(:notes)
  end

  def date_range_params
    if params[:date_range].present?
      params[:date_range].values_at(:start_date, :end_date)
    else
      [1.week.ago.to_date, Date.current]
    end
  end

  def broadcast_order_update
    Turbo::StreamsChannel.broadcast_update_to(
      "order_#{@order.id}",
      target: "order_#{@order.id}",
      partial: 'orders/order_row',
      locals: { order: @order }
    )
  end
end
```

## Hotwire Implementation

### Turbo Frame Views
```erb
<!-- app/views/orders/index.html.erb -->
<div class="container mx-auto px-4 py-8">
  <h1 class="text-3xl font-bold mb-8">Orders</h1>
  
  <!-- Filters with Turbo Frame -->
  <%= turbo_frame_tag "orders_filters" do %>
    <%= render 'filters', orders: @orders %>
  <% end %>

  <!-- Orders table with Turbo Frame -->
  <%= turbo_frame_tag "orders_table" do %>
    <%= render 'orders_table', orders: @orders %>
  <% end %>
</div>

<!-- app/views/orders/_filters.html.erb -->
<div class="bg-white p-6 rounded-lg shadow mb-6">
  <%= form_with url: orders_path, method: :get, class: "flex flex-wrap gap-4", data: { turbo_frame: "orders_table" } do |form| %>
    <div class="flex-1 min-w-[200px]">
      <%= form.select :customer_id, 
                     options_from_collection_for_select(Customer.all, :id, :name, params[:customer_id]),
                     { prompt: "All Customers" },
                     { class: "w-full px-3 py-2 border border-gray-300 rounded-md" } %>
    </div>
    
    <div class="flex-1 min-w-[200px]">
      <%= form.select :status,
                     Order.statuses.keys.map { |s| [s.titleize, s] },
                     { prompt: "All Statuses" },
                     { class: "w-full px-3 py-2 border border-gray-300 rounded-md" } %>
    </div>
    
    <div class="flex-1 min-w-[200px]">
      <%= form.date_field :date_range, name: "date_range[start_date]", value: @date_range&.first, 
                         class: "w-full px-3 py-2 border border-gray-300 rounded-md" %>
    </div>
    
    <div class="flex-1 min-w-[200px]">
      <%= form.date_field :date_range, name: "date_range[end_date]", value: @date_range&.last,
                         class: "w-full px-3 py-2 border border-gray-300 rounded-md" %>
    </div>
    
    <div>
      <%= form.submit "Filter Orders", class: "px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700" %>
    </div>
  <% end %>
</div>

<!-- app/views/orders/_orders_table.html.erb -->
<div class="bg-white shadow rounded-lg overflow-hidden">
  <table class="min-w-full divide-y divide-gray-200">
    <thead class="bg-gray-50">
      <tr>
        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Order</th>
        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Customer</th>
        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Items</th>
        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total</th>
        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
      </tr>
    </thead>
    <tbody class="bg-white divide-y divide-gray-200" id="orders_list">
      <%= render partial: "order_row", collection: orders, as: :order %>
    </tbody>
  </table>
  
  <!-- Pagination with Turbo Frame -->
  <%= turbo_frame_tag "pagination" do %>
    <%= paginate orders %>
  <% end %>
</div>

<!-- app/views/orders/_order_row.html.erb -->
<tr id="order_<%= order.id %>">
  <td class="px-6 py-4 whitespace-nowrap">
    <%= link_to "##{order.id}", order_path(order), 
                class: "text-blue-600 hover:text-blue-900 font-medium",
                data: { turbo_frame: "_top" } %>
  </td>
  <td class="px-6 py-4 whitespace-nowrap">
    <%= order.customer_name %>
  </td>
  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
    <%= order.item_count %>
  </td>
  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
    <%= number_to_currency(order.total_amount) %>
  </td>
  <td class="px-6 py-4 whitespace-nowrap">
    <%= render 'status_badge', status: order.status %>
  </td>
  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
    <%= order.created_at.strftime("%m/%d/%Y") %>
  </td>
  <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
    <div class="flex justify-end space-x-2">
      <%= render 'order_actions', order: order %>
    </div>
  </td>
</tr>

<!-- app/views/orders/_order_actions.html.erb -->
<% if order.pending? %>
  <%= button_to "Process", update_status_order_path(order, status: :processing), 
                method: :patch,
                class: "px-3 py-1 bg-yellow-600 text-white rounded hover:bg-yellow-700 text-xs",
                form: { data: { turbo_confirm: "Are you sure?" } } %>
<% elsif order.processing? %>
  <%= button_to "Complete", update_status_order_path(order, status: :completed), 
                method: :patch,
                class: "px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 text-xs",
                form: { data: { turbo_confirm: "Are you sure?" } } %>
<% end %>

<%= link_to "Cancel", order_path(order), 
            method: :delete,
            class: "px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700 text-xs",
            data: { turbo_confirm: "Are you sure you want to cancel this order?" } %>
```

### Stimulus Controllers
```javascript
// app/javascript/controllers/order_status_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["statusBadge", "statusSelect", "orderActions"]
  static values = { orderId: String }

  connect() {
    console.log(`Order status controller connected for order ${this.orderIdValue}`)
  }

  async updateStatus(event) {
    event.preventDefault()
    
    const newStatus = event.currentTarget.dataset.status
    const confirmMessage = this.getConfirmMessage(newStatus)
    
    if (!confirm(confirmMessage)) return
    
    try {
      const response = await this.updateOrderStatus(newStatus)
      await this.handleStatusUpdate(response, newStatus)
    } catch (error) {
      this.handleError(error)
    }
  }

  async updateOrderStatus(status) {
    const formData = new FormData()
    formData.append('status', status)
    
    const response = await fetch(`/orders/${this.orderIdValue}/update_status`, {
      method: 'POST',
      headers: {
        'X-CSRF-Token': this.getMetaValue('csrf-token'),
        'Accept': 'text/vnd.turbo-stream.html'
      },
      body: formData
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    return response
  }

  async handleStatusUpdate(response, newStatus) {
    const turboStream = await response.text()
    Turbo.renderStreamMessage(turboStream)
    
    // Update status badge
    this.updateStatusBadge(newStatus)
    
    // Update actions
    this.updateOrderActions(newStatus)
    
    // Show notification
    this.showNotification(`Order status updated to ${newStatus}`, 'success')
  }

  updateStatusBadge(status) {
    if (this.hasStatusBadgeTarget) {
      this.statusBadgeTarget.className = this.getBadgeClasses(status)
      this.statusBadgeTarget.textContent = this.formatStatus(status)
    }
  }

  updateOrderActions(status) {
    if (this.hasOrderActionsTarget) {
      // Update actions based on new status
      this.orderActionsTarget.innerHTML = this.getActionButtons(status)
    }
  }

  getBadgeClasses(status) {
    const classes = {
      pending: 'px-2 py-1 text-xs font-medium rounded-full bg-yellow-100 text-yellow-800',
      processing: 'px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800',
      completed: 'px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800',
      cancelled: 'px-2 py-1 text-xs font-medium rounded-full bg-red-100 text-red-800'
    }
    return classes[status] || classes.pending
  }

  getActionButtons(status) {
    if (status === 'pending') {
      return `
        <button type="button" data-action="click->order-status#updateStatus" 
                data-status="processing" class="px-3 py-1 bg-yellow-600 text-white rounded hover:bg-yellow-700 text-xs">
          Process
        </button>
      `
    } else if (status === 'processing') {
      return `
        <button type="button" data-action="click->order-status#updateStatus" 
                data-status="completed" class="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 text-xs">
          Complete
        </button>
      `
    }
    return ''
  }

  getConfirmMessage(status) {
    const messages = {
      processing: 'Are you sure you want to process this order?',
      completed: 'Are you sure you want to complete this order?',
      cancelled: 'Are you sure you want to cancel this order?'
    }
    return messages[status] || 'Are you sure?'
  }

  formatStatus(status) {
    return status.charAt(0).toUpperCase() + status.slice(1)
  }

  handleError(error) {
    console.error('Status update failed:', error)
    this.showNotification('Failed to update order status', 'error')
  }

  showNotification(message, type) {
    const notification = document.createElement('div')
    notification.className = `fixed top-4 right-4 p-4 rounded-md shadow-lg ${
      type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
    } z-50`
    notification.textContent = message
    document.body.appendChild(notification)
    
    setTimeout(() => {
      notification.remove()
    }, 3000)
  }

  getMetaValue(name) {
    const element = document.head.querySelector(`meta[name="${name}"]`)
    return element ? element.getAttribute('content') : null
  }
}

// app/javascript/controllers/order_form_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["itemsContainer", "totalAmount", "addItemButton"]
  static values = { itemTemplate: String, itemIdCounter: Number }

  connect() {
    this.calculateTotal()
  }

  addItem(event) {
    event.preventDefault()
    
    const template = this.itemTemplateValue.replace(/NEW_ITEM_INDEX/g, this.itemIdCounterValue)
    const tempDiv = document.createElement('div')
    tempDiv.innerHTML = template
    const newItem = tempDiv.firstElementChild
    
    this.itemsContainerTarget.appendChild(newItem)
    this.itemIdCounterValue++
    this.calculateTotal()
  }

  removeItem(event) {
    const item = event.target.closest('.order-item')
    item.remove()
    this.calculateTotal()
  }

  calculateTotal() {
    let total = 0
    
    this.itemsContainerTarget.querySelectorAll('.order-item').forEach(item => {
      const quantity = parseInt(item.querySelector('[data-order-form-target="quantity"]').value) || 0
      const unitPrice = parseFloat(item.querySelector('[data-order-form-target="unitPrice"]').value) || 0
      total += quantity * unitPrice
    })
    
    this.totalAmountTarget.textContent = `$${total.toFixed(2)}`
  }

  quantityChanged(event) {
    this.calculateTotal()
  }

  priceChanged(event) {
    this.calculateTotal()
  }
}
```

## Testing Strategies

### Modern Rails Testing
```ruby
# test/services/order_service_test.rb
require "test_helper"

class OrderServiceTest < ActiveSupport::TestCase
  def setup
    @customer = create(:customer)
    @product = create(:product, :in_stock, price: 25.00, available_quantity: 10)
  end

  def test_creates_order_successfully
    service = OrderService.new(
      customer_id: @customer.id,
      items: [
        { product_id: @product.id, quantity: 2, unit_price: 25.00 }
      ]
    )

    assert service.create
    assert service.order.persisted?
    assert_equal @customer.id, service.order.customer_id
    assert_equal 1, service.order.order_items.count
    assert_equal 50.00, service.order.total_amount
    assert_equal 'pending', service.order.status
  end

  def test_fails_with_invalid_customer
    service = OrderService.new(
      customer_id: 99999,
      items: [
        { product_id: @product.id, quantity: 1, unit_price: 25.00 }
      ]
    )

    assert_not service.create
    assert_includes service.errors[:customer_id], "can't be blank"
  end

  def test_fails_with_insufficient_stock
    service = OrderService.new(
      customer_id: @customer.id,
      items: [
        { product_id: @product.id, quantity: 15, unit_price: 25.00 }
      ]
    )

    assert_not service.create
    assert service.errors[:base].include?("Insufficient stock for product #{@product.name}")
  end

  def test_validates_minimal_items
    service = OrderService.new(customer_id: @customer.id, items: [])

    assert_not service.create
    assert_includes service.errors[:items], "is too short (minimum is 1 character)"
  end

  private

  def create(name, traits = {})
    FactoryBot.create(name, *traits)
  end
end

# test/integration/orders_test.rb
require "test_helper"

class OrdersTest < ActionDispatch::IntegrationTest
  def setup
    @customer = create(:customer)
    @product = create(:product, :in_stock, price: 50.00, available_quantity: 5)
    sign_in @customer
  end

  test "can create order with valid data" do
    visit new_order_path
    
    fill_in "Customer", with: @customer.id
    select @product.name, from: "Product"
    fill_in "Quantity", with: "2"
    click_button "Add Item"
    
    click_button "Create Order"
    
    assert_selector ".notice", text: "Order was successfully created"
    assert_text "50.00" # Total amount
  end

  test "cannot create order with insufficient stock" do
    visit new_order_path
    
    fill_in "Customer", with: @customer.id
    select @product.name, from: "Product"
    fill_in "Quantity", with: "10" # More than available
    click_button "Add Item"
    
    click_button "Create Order"
    
    assert_selector ".alert", text: "Insufficient stock"
  end

  test "can update order status via turbo stream" do
    order = create(:order, :pending, customer: @customer)
    
    visit orders_path
    
    within "#order_#{order.id}" do
      click_button "Process"
    end
    
    assert_selector ".notice", text: "Order status updated to processing"
    order.reload
    assert_equal "processing", order.status
  end

  test "pagination works with turbo frames" do
    create_list(:order, 25, customer: @customer)
    
    visit orders_path
    
    assert_selector "tbody tr", count: 20 # Default per page
    
    click_link "2"
    
    assert_selector "tbody tr", count: 5 # Remaining orders
    assert_text "Page 2"
  end

  test "filters work with turbo frames" do
    pending_orders = create_list(:order, 3, :pending, customer: @customer)
    completed_orders = create_list(:order, 2, :completed, customer: @customer)
    
    visit orders_path
    
    select "pending", from: "Status"
    click_button "Filter Orders"
    
    assert_selector "tbody tr", count: 3
    pending_orders.each { |order| assert_text order.id }
    completed_orders.each { |order| assert_no_text order.id }
  end

  private

  def create(name, traits = {})
    FactoryBot.create(name, *traits)
  end
end

# test/system/orders_system_test.rb
require "application_system_test_case"

class OrdersSystemTest < ApplicationSystemTestCase
  def setup
    @customer = create(:customer, email: "customer@example.com", password: "password")
    @product = create(:product, :in_stock, price: 30.00, available_quantity: 10)
  end

  test "complete order workflow with hotwire" do
    sign_in @customer
    visit orders_path
    
    click_link "New Order"
    
    # Add multiple items
    2.times do
      select @product.name, from: "Product"
      fill_in "Quantity", with: "2"
      click_button "Add Item"
      sleep 0.1 # Wait for Turbo Frame to update
    end
    
    # Check total calculation
    assert_text "$120.00" # 2 items * 2 quantity * $30 each
    
    click_button "Create Order"
    
    # Should redirect to order show page
    assert_current_path(order_path(Order.last))
    assert_text "Order was successfully created"
    
    # Test status update
    click_button "Process"
    assert_text "Order status updated to processing"
    
    click_button "Complete"
    assert_text "Order status updated to completed"
    
    # Verify order is completed
    assert_selector ".badge.bg-green-100", text: "completed"
  end

  test "real-time status updates with turbo streams" do
    order = create(:order, :pending, customer: @customer)
    
    sign_in @customer
    visit order_path(order)
    
    # Simulate status update from another session
    using_session(:admin) do
      admin = create(:user, :admin)
      sign_in admin
      
      visit orders_path
      within "#order_#{order.id}" do
        click_button "Process"
      end
      assert_text "processing", count: 2
    end
    
    # Check if status is updated in customer session
    within "#order_#{order.id}" do
      assert_text "processing"
    end
  end

  test "form validation works in real-time" do
    sign_in @customer
    visit new_order_path
    
    # Try to submit empty form
    click_button "Create Order"
    
    assert_text "Customer is required"
    assert_text "Order must contain at least one item"
    
    # Add valid customer
    fill_in "Customer", with: @customer.id
    
    # Try to submit without items
    click_button "Create Order"
    
    assert_no_text "Customer is required"
    assert_text "Order must contain at least one item"
  end

  private

  def create(name, traits = {})
    FactoryBot.create(name, *traits)
  end
end
```

## Common Use Cases

### API Resources
```ruby
# app/resources/order_resource.rb
class OrderResource < ApplicationResource
  attributes :id, :status, :total_amount, :created_at, :updated_at
  
  has_one :customer
  has_many :order_items
  
  attribute :formatted_total_amount do
    number_to_currency(object.total_amount)
  end
  
  attribute :item_count do
    object.order_items.sum(:quantity)
  end
  
  filter :status, apply: ->(records, value) {
    records.where(status: value) if value.present?
  }
  
  filter :customer_id, apply: ->(records, value) {
    records.where(customer_id: value) if value.present?
  }
  
  filter :date_range, apply: ->(records, value) {
    if value.present? && value[:start_date].present? && value[:end_date].present?
      records.where(created_at: value[:start_date]..value[:end_date])
    end
  }
  
  sort :created_at, :total_amount
end

# app/resources/customer_resource.rb
class CustomerResource < ApplicationResource
  attributes :id, :name, :email, :created_at
  
  has_many :orders
  
  attribute :order_count do
    object.orders.count
  end
  
  attribute :total_spent do
    Money.new(object.orders.sum(:total_amount_cents))
  end
end
```

### Background Jobs
```ruby
# app/jobs/order_confirmation_job.rb
class OrderConfirmationJob < ApplicationJob
  queue_as :default
  
  def perform(order)
    # Send email confirmation
    OrderMailer.confirmation(order).deliver_now
    
    # Update inventory
    order.order_items.each do |item|
      product = item.product
      product.decrement!(:available_quantity, item.quantity)
      
      # Create inventory record
      InventoryTransaction.create!(
        product: product,
        quantity: -item.quantity,
        transaction_type: :order,
        reference_id: order.id
      )
    end
    
    # Trigger webhooks
    OrderWebhookService.new(order).trigger_creation_webhooks
  rescue StandardError => e
    Rails.logger.error "Failed to process order confirmation for order #{order.id}: #{e.message}"
    raise
  end
end

# app/jobs/order_processing_job.rb
class OrderProcessingJob < ApplicationJob
  queue_as :high_priority
  
  def perform(order_id)
    order = Order.find(order_id)
    
    # Process payment
    PaymentProcessor.new(order).process_payment
    
    # Update order status
    order.transition_to!(:processing)
    
    # Send notifications
    OrderMailer.processing(order).deliver_later
    OrderStatusNotificationService.new(order).notify_status_change
  end
end
```

### GraphQL API
```ruby
# app/graphql/types/query_type.rb
module Types
  class QueryType < Types::BaseObject
    field :orders, [Types::OrderType], null: false do
      argument :customer_id, ID, required: false
      argument :status, String, required: false
      argument :limit, Integer, required: false, default_value: 20
      argument :offset, Integer, required: false, default_value: 0
    end
    
    def orders(customer_id: nil, status: nil, limit:, offset:)
      orders = Order.includes(:customer, :order_items)
      
      orders = orders.where(customer_id:) if customer_id.present?
      orders = orders.where(status:) if status.present?
      
      orders.limit(limit).offset(offset)
    end
    
    field :order, Types::OrderType, null: true do
      argument :id, ID, required: true
    end
    
    def order(id:)
      Order.find(id)
    end
  end
end

# app/graphql/types/order_type.rb
module Types
  class OrderType < Types::BaseObject
    field :id, ID, null: false
    field :status, String, null: false
    field :total_amount, Float, null: false
    field :formatted_total_amount, String, null: false
    field :created_at, GraphQL::Types::ISO8601DateTime, null: false
    field :customer, Types::CustomerType, null: false
    field :order_items, [Types::OrderItemType], null: false
    
    def formatted_total_amount
      number_to_currency(object.total_amount)
    end
  end
end
```

This Rails skill provides comprehensive expertise in modern Rails 7+ development, Hotwire implementation, and enterprise-grade application architecture for building dynamic, responsive web applications without traditional JavaScript frameworks.