window.__ngModules = [
  'core'
]

beforeEach () ->
    @sinon = sinon.sandbox.create()

afterEach () ->
    @sinon.restore()
