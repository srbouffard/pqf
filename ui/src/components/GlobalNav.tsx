import { useEffect, useRef } from 'react'

export default function GlobalNav() {
  const ref = useRef<HTMLDivElement>(null)
  useEffect(() => {
    // @canonical/global-nav initialises via script tag in production;
    // in the SPA we render a minimal Vanilla Framework navigation bar.
  }, [])
  return (
    <header className="p-navigation" ref={ref}>
      <div className="p-navigation__row">
        <div className="p-navigation__banner">
          <div className="p-navigation__tagged-logo">
            <a className="p-navigation__link" href="#/">
              <img
                className="p-navigation__logo-icon"
                src="https://assets.ubuntu.com/v1/5d6da5c4-logo-canonical-aubergine.svg"
                alt="Canonical"
                width="32"
                height="32"
              />
              <span className="p-navigation__logo-title">PQF</span>
            </a>
          </div>
        </div>
        <nav className="p-navigation__nav">
          <ul className="p-navigation__items">
            <li className="p-navigation__item">
              <a className="p-navigation__link" href="#/">Portfolio</a>
            </li>
            <li className="p-navigation__item">
              <a className="p-navigation__link" href="#/about">About</a>
            </li>
          </ul>
        </nav>
      </div>
    </header>
  )
}
