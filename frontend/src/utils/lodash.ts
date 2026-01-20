/**
 * Safe lodash utilities - proper ES6 module imports
 *
 * CORRECT USAGE:
 * import { get, set, merge } from '@/utils/lodash'
 *
 * This avoids the common mistake of:
 * import get from 'lodash/get'  // ❌ This fails in ES6 modules
 */

// Re-export commonly used lodash functions with proper ES6 imports
export { get, set, merge, cloneDeep, isEmpty, isEqual } from 'lodash-es'
