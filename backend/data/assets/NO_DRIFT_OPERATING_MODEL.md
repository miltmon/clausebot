# NO-DRIFT OPERATING MODEL
## 7-Day SLA Framework for Standards Compliance

---

## 🎯 **MISSION STATEMENT**

**Prevent training content from becoming stale, inaccurate, or non-compliant with current industry standards through systematic edition control, field validation, and platform reliability.**

---

## 📋 **OPERATING PRINCIPLES**

### **1. Edition Control (Zero Tolerance for Stale Content)**
- **Rule**: No content ships with outdated standard references
- **SLA**: 7 calendar days to review and update after edition change
- **Gate**: Publication blocked until all edition alerts cleared

### **2. Field Validation (Realism Over Theory)**
- **Rule**: All scenarios must reflect actual job site conditions
- **SLA**: Quarterly refresh with 20+ new scenarios per track
- **Gate**: Zero-tolerance for safety-critical content without dual sign-off

### **3. Platform Reliability (Offline-First, Fast Recovery)**
- **Rule**: Learning never stops due to technical issues
- **SLA**: <3s page load, offline capability, <5min rollback time
- **Gate**: All content must pass mobile + low-connectivity testing

---

## 👥 **ROLES & RESPONSIBILITIES**

### **Regulatory Liaison (Owner: MJ)**
**Primary Duties:**
- Subscribe to AWS/ASME/API/ASNT bulletins and RSS feeds
- Monitor official code release announcements
- Update `code_editions.is_current` flags within 24 hours of official release
- Create "No-Drift" ticket batches for affected content
- Maintain relationships with standards organizations

**Success Metrics:**
- 100% edition updates within 24 hours of official release
- Zero missed edition changes
- Proactive communication with module owners

### **Module Owners (Assigned per Program)**
**Primary Duties:**
- Clear `edition_alerts` within 7 calendar days
- Run ClauseBot GREEN quality gate before content updates
- Sign QC approval for all content changes
- Maintain content accuracy and current references
- Coordinate with subject matter experts for complex updates

**Success Metrics:**
- 95% SLA compliance (7-day resolution)
- Zero content published with edition mismatches
- 100% ClauseBot GREEN pass rate

**Current Assignments:**
- **Foundation Track**: MJ (milt@miltmonndt.com)
- **CWI Part A**: MJ (milt@miltmonndt.com)
- **CWI Part B**: MJ (milt@miltmonndt.com)
- **CWI Part C**: MJ (milt@miltmonndt.com)
- **Dual-Code**: MJ (milt@miltmonndt.com)
- **Master Program**: MJ (milt@miltmonndt.com)

### **Advisory Board (3-5 Veteran CWIs)**
**Primary Duties:**
- Monthly review of `scenario_submissions`
- Approve/curate field scenarios for training use
- Set zero-tolerance rules for safety-critical content
- Provide expert guidance on code interpretation
- Validate content accuracy and realism

**Success Metrics:**
- Monthly review completion rate: 100%
- Scenario approval rate: >80%
- Zero safety incidents from approved content

**Current Members:**
- TBD - Recruit 3-5 senior CWIs with 10+ years experience

### **QA Lead (Owner: MJ)**
**Primary Duties:**
- Run pre-release pilot testing on low-connectivity devices
- Own rollback procedures and emergency response
- Validate mobile responsiveness and accessibility
- Test offline functionality and sync capabilities
- Maintain quality gates and testing protocols

**Success Metrics:**
- 100% mobile compatibility (375px+)
- <3s page load times
- <5min rollback capability
- Zero critical bugs in production

---

## 🔄 **PROCESSES & WORKFLOWS**

### **Edition Change Process**

**Day 0: Edition Release**
1. Regulatory Liaison receives official announcement
2. Update `code_editions` table: set new edition as `is_current = true`
3. System automatically creates `edition_alerts` for all affected content
4. Email notification sent to all module owners
5. Publication gates activated for affected content

**Day 1-7: Review & Update**
1. Module owners receive alert notifications
2. Review content against new edition requirements
3. Update content references and clause citations
4. Run ClauseBot quality gate
5. Mark alerts as "in_progress" → "cleared"
6. Sign QC approval

**Day 7: SLA Check**
1. System checks for unresolved alerts
2. Overdue alerts escalated to management
3. Content remains blocked until cleared
4. Compliance report generated

**Escalation Path:**
- Day 3: Reminder email to module owner
- Day 5: CC management on reminder
- Day 7: Management escalation + content deprecation

### **Scenario Intake Process**

**Submission (Continuous)**
1. Field practitioners submit scenarios via intake form
2. System validates consent and required fields
3. Image uploads stored in secure storage
4. Submission marked as "pending" status

**Review (Monthly)**
1. Advisory board meets monthly
2. Review all pending submissions
3. Rate safety criticality (1-5 scale)
4. Approve/reject/request revision
5. Approved scenarios integrated into training

**Integration (Quarterly)**
1. Approved scenarios added to question banks
2. Content updated with new field examples
3. Old scenarios archived or updated
4. Training materials refreshed

### **Quality Gate Process**

**Pre-Release Testing**
1. Content passes edition verification
2. Mobile responsiveness test (375px+)
3. Offline functionality test
4. Accessibility compliance (WCAG AA)
5. ClauseBot accuracy validation
6. Performance test (<3s load time)

**Release Approval**
1. QA Lead signs off on testing
2. Module owner provides final QC
3. Publication gates released
4. Content goes live

**Post-Release Monitoring**
1. Sentry error monitoring active
2. User feedback collection
3. Performance metrics tracking
4. Rollback procedures ready

---

## 📊 **SUCCESS METRICS & KPIs**

### **Edition Control**
- **SLA Compliance**: 95% of alerts resolved within 7 days
- **Publication Accuracy**: 100% of content references current editions
- **Response Time**: <24 hours from edition release to alert creation

### **Field Validation**
- **Scenario Freshness**: 20+ new scenarios per track per quarter
- **Approval Rate**: >80% of submissions approved for use
- **Safety Rating**: 100% of safety-critical content (rating 4-5) requires dual sign-off

### **Platform Reliability**
- **Performance**: <3s page load time (95th percentile)
- **Availability**: 99.9% uptime
- **Mobile Compatibility**: 100% responsive at 375px+
- **Offline Capability**: Core content available offline

### **Content Quality**
- **ClauseBot Accuracy**: >85% accuracy on validation prompts
- **User Satisfaction**: >4.5/5 rating on content accuracy
- **Error Rate**: <1% critical errors in production

---

## 🚨 **EMERGENCY PROCEDURES**

### **Critical Edition Change**
**Trigger**: Major safety-related code update (e.g., crack acceptance criteria)
**Response**:
1. Immediate notification to all stakeholders
2. 24-hour emergency review cycle
3. All affected content temporarily unpublished
4. Expedited review and approval process

### **Platform Outage**
**Trigger**: >5 minute service interruption
**Response**:
1. Immediate rollback to last known good state
2. User notification via status page
3. Offline mode activation
4. Root cause analysis within 4 hours

### **Content Error Discovery**
**Trigger**: User reports critical inaccuracy
**Response**:
1. Immediate content review and validation
2. Temporary content removal if confirmed
3. Corrected content deployed within 24 hours
4. User notification and apology

---

## 📚 **TRAINING & DOCUMENTATION**

### **New Team Member Onboarding**
1. **Week 1**: Standards overview and edition control process
2. **Week 2**: Content creation and review procedures
3. **Week 3**: Quality gates and testing protocols
4. **Week 4**: Emergency procedures and escalation paths

### **Ongoing Training**
- **Monthly**: Standards update briefings
- **Quarterly**: Process improvement reviews
- **Annually**: Full system training refresh

### **Documentation Requirements**
- All processes documented in this SOP
- Video tutorials for complex procedures
- Quick reference cards for emergency procedures
- Regular documentation reviews and updates

---

## 🔧 **TOOLS & SYSTEMS**

### **Primary Systems**
- **Supabase**: Database and real-time alerts
- **ClauseBot**: Content validation and quality gates
- **Sentry**: Error monitoring and performance tracking
- **GA4**: User behavior and content performance analytics

### **Communication Tools**
- **Email**: Automated alerts and notifications
- **Slack**: Real-time coordination and emergency response
- **Calendar**: Scheduled reviews and meetings

### **Content Management**
- **Next.js**: Content delivery and offline capabilities
- **Service Workers**: Offline functionality and caching
- **Image Storage**: Secure scenario image storage

---

## 📅 **CALENDAR & SCHEDULE**

### **Daily**
- Monitor edition alerts and SLA compliance
- Check system health and performance metrics
- Review user feedback and error reports

### **Weekly**
- Module owner status check-ins
- Content performance review
- System maintenance and updates

### **Monthly**
- Advisory board scenario review meeting
- Process improvement review
- Compliance metrics reporting

### **Quarterly**
- Full content refresh and scenario integration
- System performance review
- Training material updates

### **Annually**
- Complete standards review and update
- Process optimization and improvement
- Team training refresh

---

## ✅ **IMPLEMENTATION CHECKLIST**

### **Phase 1: Foundation (Week 1)**
- [ ] Deploy Supabase schema and triggers
- [ ] Set up edition monitoring and alerts
- [ ] Assign module owners and SLA responsibilities
- [ ] Create emergency contact list and escalation paths

### **Phase 2: Content Integration (Week 2)**
- [ ] Integrate edition verification banners into all content pages
- [ ] Set up publication gates and quality controls
- [ ] Deploy scenario intake form and review workflow
- [ ] Test all quality gates and validation processes

### **Phase 3: Monitoring & Optimization (Week 3)**
- [ ] Set up performance monitoring and alerting
- [ ] Deploy error tracking and user feedback systems
- [ ] Create compliance dashboards and reporting
- [ ] Train team on all procedures and tools

### **Phase 4: Go-Live (Week 4)**
- [ ] Final testing and validation
- [ ] User acceptance testing
- [ ] Documentation review and approval
- [ ] Launch and monitor initial performance

---

## 📞 **CONTACTS & ESCALATION**

### **Primary Contacts**
- **Regulatory Liaison**: MJ (milt@miltmonndt.com)
- **QA Lead**: MJ (milt@miltmonndt.com)
- **Technical Lead**: MJ (milt@miltmonndt.com)

### **Escalation Path**
1. **Level 1**: Module owner (immediate response)
2. **Level 2**: QA Lead (within 4 hours)
3. **Level 3**: Management (within 24 hours)
4. **Level 4**: Emergency response team (immediate)

### **Emergency Contacts**
- **24/7 Support**: [Emergency contact information]
- **Standards Organizations**: [Key contacts for urgent clarifications]
- **Legal/Compliance**: [Legal team for regulatory issues]

---

**Document Version**: 1.0
**Last Updated**: [Current Date]
**Next Review**: [Date + 3 months]
**Approved By**: MJ
**Distribution**: All team members, advisory board, stakeholders
