import { fireEvent, getByText } from '@testing-library/dom'
import '@testing-library/jest-dom/extend-expect'
import { JSDOM } from 'jsdom'
import fs from 'fs'
import path from 'path'

const html = fs.readFileSync(path.resolve(__dirname, '../select-page.html'), 'utf8');

let dom
let container

describe('select-page.html', () => {
  beforeEach(() => {
    dom = new JSDOM(html, { runScripts: 'dangerously' })
    container = dom.window.document.body
  })

  it('Renders the heading and buttons.', () => {
    expect(container.querySelector('h1')).not.toBeNull()
    expect(container.querySelectorAll('button')).not.toBeNull()
    expect(getByText(container, 'Recommend New Songs')).toBeInTheDocument()
    expect(getByText(container, 'Rate Recommended Songs')).toBeInTheDocument()
    expect(getByText(container, 'Back To Login')).toBeInTheDocument()
  })
})