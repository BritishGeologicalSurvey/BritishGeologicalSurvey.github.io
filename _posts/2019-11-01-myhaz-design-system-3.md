---
title:  "Does every project need a design system? (Part 3)"
author: Paulius Tvaranavicius
categories:
  - UI-UX
tags:
  - design system
  - css
  - scss
  - sass
---

This is **part 3** in a blog series about our approach to creating a shared design system for [myHAZ-VCT PLATFORM](https://oda.bgs.ac.uk/).

- [Part 1 - What are design systems?](../myhaz-design-system-1)
- [Part 2 - Many ways to create a design system](../myhaz-design-system-2)
- Part 3 - Does every project need a design system?

## Does every project need a design system?

Overall, creating a design system from scratch wasn't a smooth ride, but it helped us achieve our goals - the three applications had a consistent and unified look, and we could focus on the interactions and user experience instead of thinking what shadows or border radius to use on each element. However, we haven't tried to apply a different theme for this platform. It might be a challenge for the future.

Creating a design system for one, even though large project can be a challenging task. For a design system to stay relevant it has to be managed and updated. Otherwise, it can go out of sync with the projects that rely on it quickly.

It's often easier, especially on smaller projects, to rely on other libraries like [Angular material](https://material.angular.io/), [bulma](https://bulma.io/), [Sematinc UI](https://semantic-ui.com/), etc. You might loose the brand unity, but you save time.

I saved the drawbacks of design systems for the end:

- they take a long time to create
- they have to be maintained to stay relevant
- they require buy-in from the whole team
- accessibility can be neglected sometimes

And a few things we learned in this process:

- Keep the design system modular - break up larger components into smaller ones.
- Focus on the small things - consistent fonts, limited color palette, limited button styles - and it will create more visual harmony on the larger scale
- Get feedback from other team members early to see whether those components work in their applications and how well they integrate with other UI elements.
- Think about accessibility early - make sure the navigation bars can be accessed using only keyboard, the headings follow each other in a descending order (h1, h2, h3...), etc.
- Add a prefix to your class names so they don't conflict with other libraries that might use the same name (.-mh-table, instead of just .table). We learned it the hard way when we found out another library was using the same class name.

If we were to do it again, we might use [Storybook](https://storybook.js.org/). It seems like a promising way to create and maintain component libraries, that is being adopted by many big name projects and organizations.

![Oprah sharing design systems with everyone](../../assets/images/2019-11-01-myhaz-design-system/design-systems-for-everyone.jpg)
*See more design systems examples at [Design Systems Repo](https://designsystemsrepo.com/design-systems/)*

However, for the benefits that design systems provide to become real you have to invest time in them, use them in more projects, make them more visible and make them more easily accessible.

Creating a new designs system for each project is not useful. Since you want to eliminate duplicate work it might be easier to rely on external libraries.

Brad Frost, in his book '[Atomic Design](http://atomicdesign.bradfrost.com/)', says that *'A design system should be a long-term commitment with the ambitious goal of revolutionizing how your organization creates digital work.'*
