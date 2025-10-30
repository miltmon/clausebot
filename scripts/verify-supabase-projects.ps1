# 🔍 Supabase Project Verification Script
# Helps identify which project your app is actually using

Write-Host "🔍 SUPABASE PROJECT VERIFICATION" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Project IDs discovered
$WRONG_PROJECT = "hqhughgdraokwmreronk"
$CORRECT_PROJECT = "ycmaukiqdxrneelerrsy"

Write-Host "📋 DISCOVERED PROJECTS:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  ❌ Wrong Project:   $WRONG_PROJECT" -ForegroundColor Red
Write-Host "  ✅ Correct Project: $CORRECT_PROJECT" -ForegroundColor Green
Write-Host ""

# Check frontend environment
Write-Host "🔍 CHECKING FRONTEND CONFIGURATION..." -ForegroundColor Yellow
Write-Host ""

# Check Vercel environment variables
Write-Host "1️⃣  VERCEL ENVIRONMENT VARIABLES" -ForegroundColor Cyan
Write-Host "   Run this command to check Vercel config:" -ForegroundColor Gray
Write-Host "   vercel env ls" -ForegroundColor White
Write-Host ""

# Check local .env
Write-Host "2️⃣  LOCAL ENVIRONMENT (.env.local)" -ForegroundColor Cyan
$envPath = "frontend\.env.local"
if (Test-Path $envPath) {
    $envContent = Get-Content $envPath | Select-String "SUPABASE"
    if ($envContent) {
        Write-Host "   Found Supabase config:" -ForegroundColor Green
        foreach ($line in $envContent) {
            if ($line -match $WRONG_PROJECT) {
                Write-Host "   ❌ $line" -ForegroundColor Red
            } elseif ($line -match $CORRECT_PROJECT) {
                Write-Host "   ✅ $line" -ForegroundColor Green
            } else {
                Write-Host "   $line" -ForegroundColor Yellow
            }
        }
    } else {
        Write-Host "   ⚠️  No Supabase configuration found" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ℹ️  No .env.local file found" -ForegroundColor Gray
}
Write-Host ""

# Check backend environment
Write-Host "3️⃣  BACKEND ENVIRONMENT (Render)" -ForegroundColor Cyan
Write-Host "   Check Render Dashboard for SUPABASE_URL:" -ForegroundColor Gray
Write-Host "   https://dashboard.render.com/web/srv-YOUR_SERVICE_ID" -ForegroundColor White
Write-Host ""

# Supabase Dashboard Links
Write-Host "🎯 SUPABASE DASHBOARD ACCESS" -ForegroundColor Yellow
Write-Host ""
Write-Host "✅ CORRECT PROJECT (Working System):" -ForegroundColor Green
Write-Host "   https://supabase.com/dashboard/project/$CORRECT_PROJECT" -ForegroundColor White
Write-Host ""
Write-Host "   Check these tables:" -ForegroundColor Gray
Write-Host "   • subscription_access (should have 9 test users)" -ForegroundColor White
Write-Host "   • users (test accounts)" -ForegroundColor White
Write-Host "   • quiz_items (quiz questions)" -ForegroundColor White
Write-Host ""

Write-Host "❌ WRONG PROJECT (Empty/Old Data):" -ForegroundColor Red
Write-Host "   https://supabase.com/dashboard/project/$WRONG_PROJECT" -ForegroundColor White
Write-Host ""

# Next Steps
Write-Host "📋 VERIFICATION CHECKLIST" -ForegroundColor Yellow
Write-Host ""
Write-Host "[ ] 1. Access correct Supabase project ($CORRECT_PROJECT)" -ForegroundColor White
Write-Host "[ ] 2. Check subscription_access table for test users" -ForegroundColor White
Write-Host "[ ] 3. Verify webhook logs show successful processing" -ForegroundColor White
Write-Host "[ ] 4. Check Vercel env vars point to correct project" -ForegroundColor White
Write-Host "[ ] 5. Update Render backend env vars if needed" -ForegroundColor White
Write-Host ""

# Configuration Fix
Write-Host "🔧 TO FIX CONFIGURATION:" -ForegroundColor Yellow
Write-Host ""
Write-Host "If your environment is pointing to the WRONG project:" -ForegroundColor White
Write-Host ""
Write-Host "1. Update Vercel Environment Variables:" -ForegroundColor Cyan
Write-Host "   vercel env rm VITE_SUPABASE_URL production" -ForegroundColor Gray
Write-Host "   vercel env add VITE_SUPABASE_URL production" -ForegroundColor Gray
Write-Host "   (Enter: https://$CORRECT_PROJECT.supabase.co)" -ForegroundColor White
Write-Host ""
Write-Host "2. Update Backend (Render) Environment:" -ForegroundColor Cyan
Write-Host "   • Go to Render Dashboard" -ForegroundColor Gray
Write-Host "   • Environment tab" -ForegroundColor Gray
Write-Host "   • Update SUPABASE_URL to correct project" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Redeploy both frontend and backend" -ForegroundColor Cyan
Write-Host ""

# Database Comparison
Write-Host "🔍 WHAT TO LOOK FOR IN CORRECT PROJECT:" -ForegroundColor Yellow
Write-Host ""
Write-Host "Expected Data in ycmaukiqdxrneelerrsy:" -ForegroundColor Green
Write-Host "  ✅ subscription_access table with records" -ForegroundColor White
Write-Host "  ✅ Test users: test+auth@clausebot.ai, test+fixed@clausebot.ai" -ForegroundColor White
Write-Host "  ✅ Subscription status: 'trialing' (7-day trials)" -ForegroundColor White
Write-Host "  ✅ Webhook logs showing successful events" -ForegroundColor White
Write-Host "  ✅ Customer IDs linked to Stripe" -ForegroundColor White
Write-Host ""

Write-Host "🎉 CONCLUSION" -ForegroundColor Green
Write-Host ""
Write-Host "If you find data in the CORRECT project ($CORRECT_PROJECT):" -ForegroundColor White
Write-Host "  • Your revenue system has been working all along! 🎉" -ForegroundColor Green
Write-Host "  • You were just checking the wrong database" -ForegroundColor Yellow
Write-Host "  • Update your env configs to point to the correct project" -ForegroundColor Cyan
Write-Host "  • Nov 10 launch is ON TRACK! 🚀" -ForegroundColor Green
Write-Host ""

Write-Host "Press Enter to open Supabase dashboards in browser..." -ForegroundColor Gray
$null = Read-Host

# Open browsers
Start-Process "https://supabase.com/dashboard/project/$CORRECT_PROJECT"
Start-Process "https://supabase.com/dashboard/project/$WRONG_PROJECT"

Write-Host ""
Write-Host "✅ Opened both Supabase projects in your browser" -ForegroundColor Green
Write-Host "Compare the data and report back!" -ForegroundColor Yellow

