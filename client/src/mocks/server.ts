import { setupServer } from 'msw/node'
import { handlers } from './handlers'

/**
 * Method to set up the mock server with all the defined handlers
 */
export const server = setupServer(...handlers)