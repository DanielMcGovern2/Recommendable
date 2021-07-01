import { fireEvent, getByText } from '@testing-library/dom'
import '@testing-library/jest-dom/extend-expect'
import { JSDOM } from 'jsdom'
import fs from 'fs'
import path from 'path'

const html = fs.readFileSync(path.resolve(__dirname, '../recommend-songs.html'), 'utf8');

let dom
let container

describe('recommend-songs.html', () => {
  beforeEach(() => {
    dom = new JSDOM(html, { runScripts: 'dangerously' })
    container = dom.window.document.body
  })

  it('Renders the heading and buttons.', () => {
    expect(container.querySelector('h1')).not.toBeNull()
    expect(container.querySelectorAll('button')).not.toBeNull()
    expect(getByText(container, 'Recommend New Songs')).toBeInTheDocument()
    expect(getByText(container, 'Recommend with Spotify')).toBeInTheDocument()
    expect(getByText(container, 'Recommend with Recommendable')).toBeInTheDocument()
    expect(getByText(container, 'Back')).toBeInTheDocument()
  })

  it('Hides form on render.', async () => {
    const button = getByText(container, 'Recommend with Spotify')
    expect(button).not.toBeNull()
    
    let form = container.querySelector('#rec')
    expect(form).toHaveStyle({
      display: "none"
    })
    expect(form).not.toBeVisible()
  })
})