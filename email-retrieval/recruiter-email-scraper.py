#!/usr/bin/env python3
"""
Recruiter Email Scraper
Scrapes recruiter information from https://recruiterdb.web.app/
"""

import asyncio
from playwright.async_api import async_playwright
import time


async def scrape_recruiters(load_more_clicks=25):
    """
    Scrape recruiter information from the website
    
    Args:
        load_more_clicks (int): Number of times to click "Load More" button
    """
    async with async_playwright() as p:
        print("Launching browser...")
        
        # Try simpler browser launch first
        try:
            # Launch browser with persistent user data (saves cookies/login between runs)
            browser = await p.chromium.launch_persistent_context(
                user_data_dir="./browser_data",  # This folder will store your login/cookies
                headless=False,
                timeout=30000,  # 30 second timeout
                args=[
                    "--no-sandbox",
                    "--disable-blink-features=AutomationControlled",  # Hide automation detection
                    "--disable-web-security",
                    "--disable-features=VizDisplayCompositor",
                    "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                ]
            )
            print("✓ Browser launched successfully")
        except Exception as browser_error:
            print(f"❌ Browser launch failed: {browser_error}")
            print("Trying fallback browser launch...")
            
            # Fallback - simpler launch
            try:
                browser = await p.chromium.launch(headless=False)
                context = await browser.new_context()
                page = await context.new_page()
                print("✓ Fallback browser launched")
            except Exception as fallback_error:
                print(f"❌ Fallback also failed: {fallback_error}")
                return []
        
        # Get page reference
        if hasattr(browser, 'pages'):
            page = browser.pages[0] if browser.pages else await browser.new_page()
        
        print(f"✓ Browser ready, page created")
        
        try:
            print("Navigating to recruiterdb.web.app...")
            
            # Add timeout and more detailed error handling
            try:
                await page.goto("https://recruiterdb.web.app/", timeout=30000)  # 30 second timeout
                print("✓ Navigation completed")
            except Exception as nav_error:
                print(f"❌ Navigation failed: {nav_error}")
                print("Trying alternative approach...")
                
                # Try with different options
                try:
                    await page.goto("https://recruiterdb.web.app/", 
                                  wait_until="domcontentloaded", 
                                  timeout=60000)
                    print("✓ Navigation completed with domcontentloaded")
                except Exception as alt_error:
                    print(f"❌ Alternative navigation also failed: {alt_error}")
                    return []
            
            # Check if we're actually on the right page
            current_url = page.url
            print(f"Current URL: {current_url}")
            
            if "recruiterdb.web.app" not in current_url:
                print("❌ Not on the expected website")
                return []
            
            # Wait for the page to load with much shorter timeout
            print("Waiting for page to load...")
            try:
                await page.wait_for_load_state("domcontentloaded", timeout=3000)  # Just 3 seconds
                print("✓ Page loaded successfully")
            except Exception as load_error:
                print(f" Load timeout (continuing anyway): {load_error}")
                # Continue anyway - the page might be ready
            
            # Quick check - can we find any content?
            body_content = await page.query_selector("body")
            if body_content:
                text_sample = await body_content.inner_text()
                print(f"✓ Page has {len(text_sample)} characters of content")
                if len(text_sample) < 100:
                    print(f"Sample text: {text_sample[:200]}...")
            else:
                print("❌ No body content found")
            
            # Click "Load More" button multiple times
            for i in range(load_more_clicks):
                try:
                    print(f"Looking for 'Load More' button (attempt {i+1}/{load_more_clicks})...")
                    
                    # Wait for and click the Load More button
                    # We'll try different possible selectors for the Load More button
                    load_more_selectors = [
                        "button:has-text('Load More')",
                        "button:has-text('Load more')",
                        "button:has-text('LOAD MORE')",
                        "[data-testid*='load-more']",
                        ".load-more-button",
                        "button[class*='load']"
                    ]
                    
                    button_found = False
                    for selector in load_more_selectors:
                        try:
                            await page.wait_for_selector(selector, timeout=3000)
                            print(f"Found Load More button with selector: {selector}")
                            await page.click(selector)
                            button_found = True
                            break
                        except:
                            continue
                    
                    if not button_found:
                        print("Load More button not found with any selector. Checking page content...")
                        # Get all buttons on the page to debug
                        buttons = await page.query_selector_all("button")
                        print(f"Found {len(buttons)} buttons on the page")
                        for idx, button in enumerate(buttons[:5]):  # Show first 5 buttons
                            text = await button.inner_text()
                            print(f"Button {idx + 1}: '{text}'")
                        break
                    
                    print(f"Clicked Load More button (click {i+1})")
                    
                    # Load more button delay
                    await asyncio.sleep(0.1) 
                    
                except Exception as e:
                    print(f"Error clicking Load More button on attempt {i+1}: {e}")
                    break
            
            # Extract recruiter data using the correct XPath
            print("\n--- Extracting Recruiter Data with XPath ---")
            
            # Wait a bit more for dynamic content
            await asyncio.sleep(3)
            
            # Use the XPath structure you provided
            table_xpath = "xpath=//*[@id='root']/div/div/div/div/div[2]/div/table/tbody"
            
            try:
                # First check if the table exists
                table = await page.query_selector(table_xpath)
                if not table:
                    print("❌ Table not found with XPath")
                    return []
                
                print("✓ Found table with XPath")
                
                # Get all rows in the table
                rows_xpath = "xpath=//*[@id='root']/div/div/div/div/div[2]/div/table/tbody/tr"
                rows = await page.query_selector_all(rows_xpath)
                print(f"Found {len(rows)} rows in table")
                
                recruiters = []
                
                for i, row in enumerate(rows):
                    try:
                        # Get all td elements in this row
                        cells_xpath = f"xpath=//*[@id='root']/div/div/div/div/div[2]/div/table/tbody/tr[{i+1}]/td"
                        cells = await page.query_selector_all(cells_xpath)
                        
                        print(f"Row {i+1}: Found {len(cells)} cells")
                        
                        if len(cells) >= 6:  # Should have checkbox, name, company, title, email, linkedin
                            # Extract data from specific cells
                            name_xpath = f"xpath=//*[@id='root']/div/div/div/div/div[2]/div/table/tbody/tr[{i+1}]/td[2]"
                            company_xpath = f"xpath=//*[@id='root']/div/div/div/div/div[2]/div/table/tbody/tr[{i+1}]/td[3]"
                            title_xpath = f"xpath=//*[@id='root']/div/div/div/div/div[2]/div/table/tbody/tr[{i+1}]/td[4]"
                            
                            name_elem = await page.query_selector(name_xpath)
                            company_elem = await page.query_selector(company_xpath)
                            title_elem = await page.query_selector(title_xpath)
                            
                            if name_elem and company_elem and title_elem:
                                name = await name_elem.inner_text()
                                company = await company_elem.inner_text()
                                title = await title_elem.inner_text()
                                
                                name = name.strip()
                                company = company.strip()
                                title = title.strip()
                                
                                if name and name not in ["Name", ""]:  # Skip header or empty
                                    # Try to get email - look for JavaScript data or intercept click events
                                    email = ""
                                    print(f"    🔍 Looking for email data for row {i+1}...")
                                    
                                    # Try to find email data in JavaScript variables on the page
                                    try:
                                        # Check if there's recruiter data stored in JavaScript
                                        js_data = await page.evaluate("""
                                            () => {
                                                // Look for common variable names that might store recruiter data
                                                const possibleVars = ['recruiters', 'data', 'tableData', 'recruiterData', 'contacts'];
                                                for (let varName of possibleVars) {
                                                    if (window[varName]) {
                                                        return window[varName];
                                                    }
                                                }
                                                
                                                // Also check React props or state
                                                const rootElement = document.getElementById('root');
                                                if (rootElement && rootElement._reactInternalFiber) {
                                                    // Try to find React data
                                                    return 'react_data_found';
                                                }
                                                
                                                return null;
                                            }
                                        """)
                                        
                                        if js_data:
                                            print(f"      Found JS data: {str(js_data)[:200]}...")
                                            
                                            # If it's an array, try to get the email from the current row index
                                            if isinstance(js_data, list) and len(js_data) > i:
                                                recruiter_data = js_data[i]
                                                if isinstance(recruiter_data, dict):
                                                    # Look for email in common field names
                                                    for key in ['email', 'mail', 'contact', 'e_mail']:
                                                        if key in recruiter_data:
                                                            email = recruiter_data[key]
                                                            break
                                    except Exception as e:
                                        print(f"      Error checking JS data: {e}")
                                    
                                    # If no JS data found, try clicking the button and intercepting the action
                                    if not email:
                                        try:
                                            print(f"      Trying to intercept email button click for row {i+1}...")
                                            
                                            # Set up listener for window.open or location changes
                                            await page.evaluate("""
                                                () => {
                                                    window.lastEmailAction = '';
                                                    
                                                    // Override window.open to capture mailto links
                                                    const originalOpen = window.open;
                                                    window.open = function(url, ...args) {
                                                        if (url && url.startsWith('mailto:')) {
                                                            window.lastEmailAction = url;
                                                            return null; // Don't actually open
                                                        }
                                                        return originalOpen.call(this, url, ...args);
                                                    };
                                                    
                                                    // Also override location assignment
                                                    const originalAssign = location.assign;
                                                    location.assign = function(url) {
                                                        if (url && url.startsWith('mailto:')) {
                                                            window.lastEmailAction = url;
                                                            return;
                                                        }
                                                        return originalAssign.call(this, url);
                                                    };
                                                }
                                            """)
                                            
                                            # Click the email button
                                            email_button_xpath = f"xpath=//*[@id='root']/div/div/div/div/div[2]/div/table/tbody/tr[{i+1}]/td[5]/div/button"
                                            email_button = await page.query_selector(email_button_xpath)
                                            
                                            if email_button:
                                                await email_button.click()
                                                await asyncio.sleep(0.1)  # Brief pause to let JS run
                                                
                                                # Check if we intercepted a mailto link
                                                email_action = await page.evaluate("() => window.lastEmailAction")
                                                
                                                if email_action and "mailto:" in email_action:
                                                    email = email_action.replace("mailto:", "").split("?")[0]
                                                    print(f"      ✓ Intercepted email: {email}")
                                                else:
                                                    print(f"      No mailto intercepted: '{email_action}'")
                                            
                                        except Exception as e:
                                            print(f"      Error intercepting email: {e}")
                                    
                                    # Similar approach for LinkedIn
                                    linkedin = ""
                                    print(f"    🔍 Looking for LinkedIn data for row {i+1}...")
                                    
                                    # Try JS data first
                                    if js_data and isinstance(js_data, list) and len(js_data) > i:
                                        recruiter_data = js_data[i]
                                        if isinstance(recruiter_data, dict):
                                            for key in ['linkedin', 'linkedIn', 'profile', 'social']:
                                                if key in recruiter_data:
                                                    linkedin = recruiter_data[key]
                                                    break
                                    
                                    # If no JS data, try intercepting LinkedIn button
                                    if not linkedin:
                                        try:
                                            print(f"      Trying to intercept LinkedIn button click for row {i+1}...")
                                            
                                            # Set up listener for LinkedIn URLs
                                            await page.evaluate("""
                                                () => {
                                                    window.lastLinkedInAction = '';
                                                    
                                                    const originalOpen = window.open;
                                                    window.open = function(url, ...args) {
                                                        if (url && url.includes('linkedin.com')) {
                                                            window.lastLinkedInAction = url;
                                                            return null; // Don't actually open
                                                        }
                                                        return originalOpen.call(this, url, ...args);
                                                    };
                                                }
                                            """)
                                            
                                            # Click the LinkedIn button
                                            linkedin_button_xpath = f"xpath=//*[@id='root']/div/div/div/div/div[2]/div/table/tbody/tr[{i+1}]/td[6]/button"
                                            linkedin_button = await page.query_selector(linkedin_button_xpath)
                                            
                                            if linkedin_button:
                                                await linkedin_button.click()
                                                await asyncio.sleep(0.1)  # Brief pause
                                                
                                                # Check if we intercepted a LinkedIn URL
                                                linkedin_action = await page.evaluate("() => window.lastLinkedInAction")
                                                
                                                if linkedin_action and "linkedin.com" in linkedin_action:
                                                    linkedin = linkedin_action
                                                    print(f"      ✓ Intercepted LinkedIn: {linkedin}")
                                                else:
                                                    print(f"      No LinkedIn intercepted: '{linkedin_action}'")
                                            
                                        except Exception as e:
                                            print(f"      Error intercepting LinkedIn: {e}")
                                    
                                    recruiter_data = {
                                        "name": name,
                                        "company": company,
                                        "title": title,
                                        "email": email,
                                        "linkedin": linkedin
                                    }
                                    recruiters.append(recruiter_data)
                                    print(f"✓ Row {i+1}: {name} - {company} - {title}")
                                    if email:
                                        print(f"    📧 Email: {email}")
                                    if linkedin:
                                        print(f"    💼 LinkedIn: {linkedin}")
                                else:
                                    print(f"  Row {i+1}: Skipped (header or empty)")
                            else:
                                print(f"  Row {i+1}: Could not find name/company/title elements")
                                
                    except Exception as e:
                        print(f"  Row {i+1} error: {e}")
                        continue
                
                print(f"\n--- Summary ---")
                print(f"Successfully extracted {len(recruiters)} recruiters")
                
                return recruiters
                
            except Exception as e:
                print(f"Error with XPath extraction: {e}")
                
                # Fallback - take screenshot for debugging
                try:
                    await page.screenshot(path="page_debug.png")
                    print("📸 Screenshot saved as 'page_debug.png'")
                except:
                    pass
                    
                return []
            
        except Exception as e:
            print(f"Error during scraping: {e}")
            return []
        finally:
            await browser.close()


if __name__ == "__main__":
    print("Starting Recruiter Email Scraper...")
    recruiters = asyncio.run(scrape_recruiters(load_more_clicks=21)) # End of page reached after 21 clicks
    
    # Optional: Save data to a file
    if recruiters:
        import json
        with open("recruiters_data.json", "w") as f:
            json.dump(recruiters, f, indent=2)
        print(f"\nData saved to recruiters_data.json ({len(recruiters)} recruiters)")
