import React from "react"
import clsx from "clsx"
import styles from "./styles.module.css"

const FeatureList = [
  {
    title: "Understand feature parity",
    // Svg: require('@site/static/img/undraw_docusaurus_mountain.svg').default,
    description: (
      <>
        Enable users to be able to easily see what features and functionality is
        available across the supported languages. Enable maintainers to be able
        to see gaps to fill.
      </>
    ),
  },
  {
    title: "Unlock Community Contributions",
    // Svg: require('@site/static/img/undraw_docusaurus_tree.svg').default,
    description: (
      <>
        Provide reference examples of new features and functionality with tests
        to work against, so that more people will be able to contribute without
        the huge overhead of trying to understand what to do, and where to
        begin!
      </>
    ),
  },
  {
    title: "Improve cross-language support",
    // Svg: require('@site/static/img/undraw_docusaurus_tree.svg').default,
    description: (
      <>
        Reduce the overhead of maintainers being able to understand and assist
        with a problem in a non-preferred language, by being able to see
        side-by-side how something exactly equivalent would be implemented in
        different languages.
      </>
    ),
  },
]

function Feature({ Svg, title, description }) {
  return (
    <div className={clsx("col col--4")}>
      {/*<div className="text--center">*/}
      {/*  <Svg className={styles.featureSvg} role="img" />*/}
      {/*</div>*/}
      <div className="text--center padding-horiz--md">
        <h3>{title}</h3>
        <p>{description}</p>
      </div>
    </div>
  )
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  )
}
