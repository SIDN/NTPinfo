import { server } from '../mocks/server'
import { beforeAll, afterAll, afterEach } from 'vitest'

/**
 * File to setup the mock server for the tests to call
 */

beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())