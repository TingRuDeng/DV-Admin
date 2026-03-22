import { describe, it, expect, beforeEach } from 'vitest'
import { Storage } from '@/utils/storage'

describe('storage utils', () => {
  beforeEach(() => {
    localStorage.clear()
    sessionStorage.clear()
  })

  describe('Storage.set and Storage.get', () => {
    it('should set and get a string value', () => {
      Storage.set('test-key', 'test-value')
      expect(Storage.get('test-key')).toBe('test-value')
    })

    it('should set and get a number value', () => {
      Storage.set('number-key', 123)
      expect(Storage.get('number-key')).toBe(123)
    })

    it('should set and get an object value', () => {
      const obj = { name: 'test', value: 123 }
      Storage.set('object-key', obj)
      expect(Storage.get('object-key')).toEqual(obj)
    })

    it('should return default value when key not found', () => {
      expect(Storage.get('non-existent', 'default')).toBe('default')
    })
  })

  describe('Storage.remove', () => {
    it('should remove a specific key', () => {
      Storage.set('to-remove', 'value')
      Storage.remove('to-remove')
      expect(Storage.get('to-remove')).toBeFalsy()
    })
  })

  describe('Storage.sessionSet and Storage.sessionGet', () => {
    it('should set and get session value', () => {
      Storage.sessionSet('session-key', 'session-value')
      expect(Storage.sessionGet('session-key')).toBe('session-value')
    })
  })

  describe('Storage.clear', () => {
    it('should clear a specific key from both storages', () => {
      Storage.set('key1', 'value1')
      Storage.sessionSet('key1', 'value1')
      Storage.clear('key1')
      expect(Storage.get('key1')).toBeFalsy()
      expect(Storage.sessionGet('key1')).toBeFalsy()
    })
  })
})
