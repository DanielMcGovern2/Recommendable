import { fireEvent, getByText } from '@testing-library/dom'
import '@testing-library/jest-dom/extend-expect'
import { JSDOM } from 'jsdom'
import fs from 'fs'
import path from 'path'

const html = fs.readFileSync(path.resolve(__dirname, '../rate-songs.html'), 'utf8');

let dom
let container

describe('rate-songs.html', () => {
  beforeEach(() => {
    dom = new JSDOM(html, { runScripts: 'dangerously' })
    container = dom.window.document.body
  })

  it('Renders the heading and buttons.', () => {
    expect(container.querySelector('h1')).not.toBeNull()
    expect(container.querySelectorAll('button')).not.toBeNull()
    expect(container.querySelectorAll('p')).not.toBeNull()
    expect(container.querySelectorAll('form')).not.toBeNull()
    expect(getByText(container, 'Rate')).toBeInTheDocument()
    expect(getByText(container, 'Submit')).toBeInTheDocument()
    expect(getByText(container, 'Back')).toBeInTheDocument()
  })

  it('Disables \'Submit\' on render.', async () => {
    expect(getByText(container, 'Submit')).toBeDisabled()
  })
})