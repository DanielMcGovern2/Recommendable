import { fireEvent, getByText } from '@testing-library/dom'
import '@testing-library/jest-dom/extend-expect'
import { JSDOM } from 'jsdom'
import fs from 'fs'
import path from 'path'

const html = fs.readFileSync(path.resolve(__dirname, '../index.html'), 'utf8');

let dom
let container

describe('index.html', () => {
  beforeEach(() => {
    dom = new JSDOM(html, { runScripts: 'dangerously' })
    container = dom.window.document.body
  })

  it('Renders the heading and buttons.', () => {
    expect(container.querySelector('h3')).not.toBeNull()
    expect(container.querySelectorAll('button')).not.toBeNull()
    expect(getByText(container, 'Log in with Spotify')).toBeInTheDocument()
    expect(getByText(container, 'Begin')).toBeInTheDocument()
  })

  it('Hides \'Begin\' on render.', async () => {
    expect(getByText(container, 'Begin')).not.toBeVisible()
  })
})