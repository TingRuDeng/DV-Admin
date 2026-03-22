import { describe, it, expect } from 'vitest'

describe('basic tests', () => {
  it('should pass basic assertion', () => {
    expect(1 + 1).toBe(2)
  })

  it('should handle string operations', () => {
    const str = 'hello world'
    expect(str.includes('hello')).toBe(true)
    expect(str.toUpperCase()).toBe('HELLO WORLD')
  })

  it('should handle array operations', () => {
    const arr = [1, 2, 3, 4, 5]
    expect(arr.filter((n) => n > 2)).toEqual([3, 4, 5])
    expect(arr.map((n) => n * 2)).toEqual([2, 4, 6, 8, 10])
  })

  it('should handle object operations', () => {
    const obj = { name: 'test', value: 123 }
    expect(obj.name).toBe('test')
    expect({ ...obj, value: 456 }).toEqual({ name: 'test', value: 456 })
  })
})
